import pytest

from src.processor.utils.transform_data import transform_sales_order


class TestTransformSalesOrder():
    @pytest.fixture
    def test_sales_data(self):
        test_input_sales_data = [{
            "sales_order_id": "1",
            "created_at": "2022-11-03 14:20:52.186",
            "last_updated": "2022-11-03 14:20:52.186",
            "design_id": "9",
            "staff_id": "16",
            "counterparty_id": "18",
            "units_sold": "84754",
            "unit_price": "2.43",
            "currency_id": "3",
            "agreed_delivery_date": "2022-11-10",
            "agreed_payment_date": "2022-11-03",
            "agreed_delivery_location_id": "4",
        }]
        test_output_sales_data = [{
            "sales_order_id": "1",
            "created_date": "2022-11-03",
            "created_time": "14:20:52.186",
            "last_updated_date": "2022-11-03",
            "last_updated_time": "14:20:52.186",
            "sales_staff_id": "16",
            "counterparty_id": "18",
            "units_sold": "84754",
            "unit_price": "2.43",
            "currency_id": "3",
            "design_id": "9",
            "agreed_payment_date": "2022-11-03",
            "agreed_delivery_date": "2022-11-10",
            "agreed_delivery_location_id": "4",
        }]

        return test_input_sales_data, test_output_sales_data

    def test_returns_list_of_dictionaries(self, test_sales_data):
        test_input_sales_data, test_output_sales_data = test_sales_data

        result = transform_sales_order(test_input_sales_data)

        assert isinstance(result, list)

        for item in result:
            assert isinstance(item, dict)

    def test_returns_empty_list_if_passed_file_with_no_data(
        self,
        test_sales_data
    ):
        test_input_sales_data, test_output_sales_data = test_sales_data

        result = transform_sales_order(test_input_sales_data)

        assert result == []

    def test_returns_contents_of_csv_as_list_of_dictionaries(
        self,
        test_sales_data
    ):
        test_input_sales_data, test_output_sales_data = test_sales_data

        result = transform_sales_order(test_input_sales_data)
        expected = test_output_sales_data

        assert result == expected
