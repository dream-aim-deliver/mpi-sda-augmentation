from pydantic import BaseModel, Field
from datetime import date

class QueryModel(BaseModel):
    """
    A model representing geographical coordinates.

    Attributes:
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.
    """
    latitude: float
    longitude: float

class DataSourceModel(BaseModel):
    """
    A model representing a data source.

    Attributes:
        source (str): The name or identifier of the data source.
        q (QueryModel): The QueryModel instance containing latitude and longitude.
    """
    source: str
    q: QueryModel

class PipelineRequestModel(BaseModel):
    """
    A model representing a request for a pipeline process.

    Attributes:
       
        # data_sources (list[DataSourceModel]): A list of DataSourceModel instances (uncomment if needed).
    """
    start_date: date = Field(default_factory=date.today)
    end_date: date = Field(default_factory=date.today)

class SentinelHubRequest(PipelineRequestModel):
    """
    A model extending PipelineRequestModel specifically for Sentinel Hub requests.

    Attributes:
      
        q (QueryModel): A QueryModel instance representing geographical coordinates for the Sentinel Hub request.
    """
    q: QueryModel
