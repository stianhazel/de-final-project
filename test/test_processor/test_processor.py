import pytest
from unittest.mock import patch

from botocore.exceptions import ClientError
from pg8000.exceptions import InterfaceError


from src.processor.processor import lambda_handler


@pytest.fixture
def test_data():
    return [
        {"id": "1", "firstname": "Rosanne", "lastname": "Harriman"},
        {"id": "2", "firstname": "Hermione", "lastname": "Leler"},
        {"id": "3", "firstname": "Bernardine", "lastname": "Cosenza"},
    ]


@patch("src.processor.processor.convert_and_dump_parquet")
@patch("src.processor.processor.transform_data")
@patch("src.processor.processor.read_csv")
class TestUtilFunctions:
    def test_lambda_calls_util_functions_with_correct_args(
        self, mock_read, mock_transform, mock_convert_and_dump, test_data
    ):
        bucket_name = "processed-20231103142232905400000002"

        mock_read.return_value = test_data
        mock_transform.return_value = test_data

        lambda_handler(
            event={"Records":
                   [{"s3": {"object": {"key": "test_path/test_name.csv"}}}]},
            context=None,
        )
        "read_csv is called with filename and bucket name"
        mock_read.assert_called_once_with("test_path/test_name.csv",
                                          bucket_name)

        "transform_data is called with the data read from csv"
        mock_transform.assert_called_once_with(test_data)

        """convert_and_dump_parquet is called with filename, transformed_data
         and bucket_name"""
        mock_convert_and_dump.assert_called_once_with(
            "test_path/test_name.csv", test_data, bucket_name
        )


@patch("src.processor.processor.logger")
@patch("src.processor.processor.convert_and_dump_parquet")
@patch("src.processor.processor.transform_data")
@patch("src.processor.processor.read_csv")
class TestLogging:
    def test_logs_correct_info(
        self, mock_read,
        mock_transform,
        mock_convert_and_dump,
        mock_logger,
        test_data
    ):
        test_filename = "test_path/test_name.parquet"
        bucket_name = "processed-20231103142232905400000002"

        mock_read.return_value = test_data
        mock_transform.return_value = test_data
        mock_convert_and_dump.return_value = test_filename

        lambda_handler(
            event={"Records":
                   [{"s3": {"object": {"key": "test_path/test_name.csv"}}}]},
            context=None,
        )

        mock_logger.info.assert_called_once_with(
            f"File {test_filename} added to bucket {bucket_name}"
        )

    def test_when_error_with_source_db_logs_correct_error_message(
        self,
        mock_read,
        mock_transform,
        mock_convert_and_dump,
        mock_logger,
        test_data
    ):
        mock_read.return_value = test_data
        mock_transform.side_effect = InterfaceError

        lambda_handler(
            event={"Records":
                   [{"s3": {"object": {"key": "test_path/test_name.csv"}}}]},
            context=None,
        )

        mock_logger.error.assert_called_once_with(
            "Error interacting with database.")

    def test_when_error_finding_a_secret_logs_correct_error_message(
        self,
        mock_read,
        mock_transform,
        mock_convert_and_dump,
        mock_logger,
        test_data
    ):
        mock_read.return_value = test_data
        mock_transform.side_effect = ClientError(
            {
                "Error": {
                    "Code": "ResourceNotFoundException",
                }
            },
            "Operation name",
        )

        lambda_handler(
            event={"Records":
                   [{"s3": {"object": {"key": "test_path/test_name.csv"}}}]},
            context=None,
        )

        mock_logger.error.assert_called_once_with(
            "Error getting database credentials from Secrets Manager."
        )

    def test_when_error_accessing_a_bucket_logs_correct_error_message(
        self,
        mock_read,
        mock_transform,
        mock_convert_and_dump,
        mock_logger,
        test_data
    ):
        mock_read.side_effect = ClientError(
            {
                "Error": {
                    "Code": "NoSuchBucket",
                }
            },
            "Operation name",
        )

        lambda_handler(
            event={"Records":
                   [{"s3": {"object": {"key": "test_path/test_name.csv"}}}]},
            context=None,
        )

        mock_logger.error.assert_called_once_with(
            "Error acessing the bucket. NoSuchBucket."
        )

    def test_when_general_aws_error_logs_correct_error_message(
        self,
        mock_read,
        mock_transform,
        mock_convert_and_dump,
        mock_logger,
        test_data
    ):
        mock_read.return_value = test_data
        mock_transform.return_value = test_data
        mock_convert_and_dump.side_effect = ClientError(
            {
                "Error": {
                    "Code": "SampleErrorCode",
                    "Message": "Example error message",
                }
            },
            "Operation name",
        )

        lambda_handler(
            event={"Records":
                   [{"s3": {"object": {"key": "test_path/test_name.csv"}}}]},
            context=None,
        )

        mock_logger.error.assert_called_once_with(
            "AWS client error SampleErrorCode.\nExample error message."
        )

    def test_when_general_exception_logs_correct_error_message(
        self,
        mock_read,
        mock_transform,
        mock_convert_and_dump,
        mock_logger,
        test_data
    ):
        mock_read.return_value = test_data
        mock_transform.return_value = test_data
        mock_convert_and_dump.side_effect = Exception

        lambda_handler(
            event={"Records":
                   [{"s3": {"object": {"key": "test_path/test_name.csv"}}}]},
            context=None,
        )

        mock_logger.error.assert_any_call("Unexpected error occurred.")
