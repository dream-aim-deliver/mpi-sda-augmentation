from logging import Logger
import logging
from typing import List
from app.sdk.models import KernelPlancksterSourceData, BaseJobState, JobOutput, ProtocolEnum
from app.sdk.scraped_data_repository import ScrapedDataRepository,  KernelPlancksterSourceData
import time
import os
import json
import pandas as pd
from dotenv import load_dotenv
from models import PipelineRequestModel
from numpy import ndarray
import numpy as np
import cv2
import tempfile

# Load environment variables
load_dotenv()


def augment(
    job_id: int,
    tracer_id: str,
    scraped_data_repository: ScrapedDataRepository,
    log_level: Logger,
    work_dir: str


) -> JobOutput:


    try:
        logger = logging.getLogger(__name__)
        logging.basicConfig(level=log_level)

        job_state = BaseJobState.CREATED
        protocol = scraped_data_repository.protocol
    
        # Set the job state to running
        logger.info(f"{job_id}: Starting Job")
        job_state = BaseJobState.RUNNING
        #job.touch()

        start_time = time.time()  # Record start time for response time measurement #TODO: decide wether we want this or not
        #Download all relevant files from minio
        kernel_planckster = scraped_data_repository.kernel_planckster
        source_list = kernel_planckster.list_all_source_data()

        minimum_info = {"sentinel": False, "twitter": False, "telegram": False}
        for source in source_list:
            res = download_source_if_relevant(source, job_id, tracer_id, scraped_data_repository, work_dir)
            if res["sentinel"] == True: minimum_info["sentinel"] = True; 
            elif res["twitter"] == True: minimum_info["twitter"] = True; 
            elif res["telegram"] == True: minimum_info["telegram"] = True
        
        #do matching/ augmentation
    
        if minimum_info["sentinel"] == True and minimum_info["twitter"] == True or minimum_info["sentinel"] == True and minimum_info["telegram"] == True:
            augment_by_date(work_dir, job_id, scraped_data_repository, protocol, minimum_info)
        else:
            logger.warn("Could not run augmentation, try again after running data pipeline for sentinel, twitter, and telegram")

            

                
        
    except Exception as error:
        logger.error(f"{job_id}: Unable to scrape data. Job with tracer_id {tracer_id} failed. Error:\n{error}")
        job_state = BaseJobState.FAILED
        #job.messages.append(f"Status: FAILED. Unable to scrape data. {e}")




def download_source_if_relevant(source: KernelPlancksterSourceData, job_id:int, tracer_id: str, scraped_data_repository: ScrapedDataRepository, work_dir: str):
    name = source["name"]
    protocol = source["protocol"]
    relative_path = source["relative_path"]

    #reconstruct the source_data object
    source_data = KernelPlancksterSourceData(
        name= name,
        protocol=protocol,
        relative_path=relative_path,
    )

    file_name = os.path.basename(relative_path)         

    res = {"sentinel": False, "twitter": False, "telegram": False}
    if "sentinel" in source_data.relative_path and os.path.splitext(source_data.relative_path)[1] ==".json":
        sentinel_coords_path = os.path.join(work_dir, "wildfire_coords", file_name)
        scraped_data_repository.download_json(source_data, job_id, sentinel_coords_path)
        res["sentinel"] = True

    #TODO: replace with regex
    elif "twitter" in source_data.relative_path and "data" in os.path.basename(source_data.relative_path):
        
        twitter_coords_path = os.path.join(work_dir, "twitter_augment", file_name)
        scraped_data_repository.download_json(source_data, job_id, twitter_coords_path)
        res["twitter"] = True

    elif "telegram" in source_data.relative_path and "data" in os.path.basename(source_data.relative_path):
        telegram_coords_path = os.path.join(work_dir, "telegram_augment", file_name)
        scraped_data_repository.download_json(source_data, job_id, telegram_coords_path)
        res["telegram"] = True
    
    return res

#TODO: plan system that uses generic sattelitedata() and socialfeeddata() classes
def augment_by_date(work_dir: str, job_id:int,  scraped_data_repository: ScrapedDataRepository, protocol: ProtocolEnum, minimum_info: dict ):
    key = {
    "01": "January",
    "02": "February",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December"
    }
    twitter_df=pd.DataFrame()
    telegram_df=pd.DataFrame()
    if minimum_info["twitter"]:
        latest_twitter_data = sorted([f for f in os.listdir(f'{work_dir}/twitter_augment')], key=lambda x: x[5:20], reverse=True)[0]
        twitter_df = pd.read_json(f'{work_dir}/twitter_augment/{latest_twitter_data}', orient="index")
    if minimum_info["telegram"]:
        telegram_df = pd.read_json(f'{work_dir}/telegram_augment/data.json', orient="index")
    sentinel_dir = os.path.join(work_dir, "wildfire_coords")
    
    for wildifre_coords_json_file_path in os.listdir(sentinel_dir):
        data = []
        sentinel_df= pd.read_json(os.path.join(sentinel_dir,wildifre_coords_json_file_path), orient="index")
        for index, row in sentinel_df.iloc[0:].iterrows():
            lattitude = row['latitude']
            longitude = row['longitude']
            status = row['status']
                                                       #title tweet location
            data.append([status, lattitude, longitude, "n/a", "n/a", "n/a" ])

        underscore_date=wildifre_coords_json_file_path[2:wildifre_coords_json_file_path.index("____")]
        split_date = underscore_date.split("_")
        sat_image_year = split_date[0]; sat_image_month = key[split_date[1]]; sat_image_day = split_date[2]
    
        matches_found_twitter = 0
        for index, row in twitter_df.iloc[0:].iterrows():
            tweet_title = row['Title']
            tweet_tweet = row['Tweet']
            tweet_location = row['Extracted_Location']
            tweet_latitude = row['Resolved_Latitude']
            tweet_longitude = row['Resolved_Longitude']
            tweet_month = row['Month']
            tweet_day = row['Day']
            tweet_year = row['Year']
            tweet_disaster_type = row['Disaster_Type']

            
            if(int(sat_image_year) == int(tweet_year) and sat_image_month == tweet_month and int(sat_image_day) == int(tweet_day)):
                matches_found_twitter += 1
                
                data.append([f"tweet about {tweet_disaster_type}", tweet_latitude, tweet_longitude, tweet_title, tweet_tweet, tweet_location ])
        
        matches_found_telegram = 0
        for index, row in telegram_df.iloc[0:].iterrows():
            telegram_title = row['Title']
            telegram_tweet = row['Telegram']
            telegram_location = row['Extracted_Location']
            telegram_latitude = row['Resolved_Latitude']
            telegram_longitude = row['Resolved_Longitude']
            telegram_month = row['Month']
            telegram_day = row['Day']
            telegram_year = row['Year']
            telegram_disaster_type = row['Disaster_Type']

        
            if(int(sat_image_year) == int(telegram_year) and sat_image_month == telegram_month and int(sat_image_day) == int(telegram_day)):
                matches_found_telegram += 1
                data.append([f"telegram post about {telegram_disaster_type}", telegram_latitude, telegram_longitude, telegram_title, telegram_tweet, telegram_location ])

        date_df = pd.DataFrame(data, columns=["Status", "Lattitude", "Longitude", "Title", "Text", "Location"])
        os.makedirs(f"{work_dir}/by_date", exist_ok=True)
        if matches_found_twitter >= 1 or matches_found_telegram >= 1:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            local_json_path = f"{work_dir}/by_date/{sat_image_year}_{sat_image_month}_{sat_image_day}_{timestamp}.json"
            date_df.to_json(local_json_path, orient='index', indent=4)
            
            #upload to minio
            source_data = KernelPlancksterSourceData(
            name=f"{sat_image_year}_{sat_image_month}_{sat_image_day}_{timestamp}",
            protocol=protocol,
            relative_path=f"augmented/by_date/{sat_image_year}_{sat_image_month}_{sat_image_day}_{timestamp}.json"
            )

            try:
                scraped_data_repository.register_scraped_json(
                job_id=job_id,
                source_data=source_data,
                local_file_name=local_json_path,
                )
            except Exception as e:
                continue
