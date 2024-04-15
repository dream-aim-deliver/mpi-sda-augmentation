from logging import Logger
import os
from typing import Tuple

from app.sdk.file_repository import FileRepository
from app.sdk.kernel_plackster_gateway import KernelPlancksterGateway
from app.sdk.models import ProtocolEnum


def _setup_kernel_planckster(
    job_id: int,
    logger: Logger,
    kernel_planckster_host: str,
    kernel_planckster_port: int,
    kernel_planckster_auth_token: str,
    kernel_planckster_scheme: str,
) -> KernelPlancksterGateway:

    try:

        logger.info(f"{job_id}: Setting up Kernel Planckster Gateway.")

        # Setup the Kernel Planckster Gateway
        kernel_planckster = KernelPlancksterGateway(
            host=kernel_planckster_host,
            port=kernel_planckster_port,
            auth_token=kernel_planckster_auth_token,
            scheme=kernel_planckster_scheme,
        )
        kernel_planckster.ping()
        logger.info(f"{job_id}: Kernel Planckster Gateway setup successfully.")

        return kernel_planckster

    except Exception as error:
        logger.error(
            f"{job_id}: Unable to setup the Kernel Planckster Gateway. Error:\n{error}"
        )
        raise error


def _setup_file_repository(
    job_id: int,
    storage_protocol: ProtocolEnum,
    logger: Logger,
) -> FileRepository:

    try:
        logger.info(f"{job_id}: Setting up the File Repository.")

        file_repository = FileRepository(
            protocol=storage_protocol,
        )

        logger.info(f"{job_id}: File Repository setup successfully.")

        return file_repository

    except Exception as error:
        logger.error(f"{job_id}: Unable to setup the File Repository. Error:\n{error}")
        raise error


def setup(
    job_id: int,
    logger: Logger,
    kp_auth_token: str,
    kp_host: str,
    kp_port: int,
    kp_scheme: str,
) -> Tuple[KernelPlancksterGateway, ProtocolEnum, FileRepository]:
    """
    Setup the Kernel Planckster Gateway, the storage protocol and the file repository.

    NOTE: needs and '.env' file within context.
    """

    try:
        kernel_planckster = _setup_kernel_planckster(
            job_id, logger, kp_host, kp_port, kp_auth_token, kp_scheme
        )

        logger.info(f"{job_id}: Checking storage protocol.")
        protocol = ProtocolEnum(os.getenv("STORAGE_PROTOCOL", ProtocolEnum.S3.value))


        logger.info(f"{job_id}: Storage protocol: {protocol}")

        file_repository = _setup_file_repository(job_id, protocol, logger)

        return kernel_planckster, protocol, file_repository

    except Exception as error:
        logger.error(f"{job_id}: Unable to setup. Error:\n{error}")
        raise error
