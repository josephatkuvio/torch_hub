import requests
from io import BytesIO
from PIL import Image

def recognize_text(image_path, subscription_key, endpoint):
    """
    Recognizes texts in an image using Microsoft Cognitive Services Computer Vision API.

    Args:
        image_path (str): Path to the image file.
        subscription_key (str): Subscription key for Azure Cognitive Services.
        endpoint (str): Endpoint for Azure Cognitive Services.

    Returns:
        list: A list of recognized texts extracted from the image.
    """
    # Load the image from the file
    image_data = open(image_path, "rb").read()

    # Set the API endpoint and parameters
    api_url = f"{endpoint}/vision/v3.2/read/analyze"
    headers = {
        "Content-Type": "application/octet-stream",
        "Ocp-Apim-Subscription-Key": subscription_key
    }
    params = {
        "language": "en",
        "detectOrientation": "true"
    }

    # Make a POST request to the API
    response = requests.post(api_url, headers=headers, params=params, data=image_data)

    # Check if the request was successful
    if response.status_code == 202:
        # Get the operation ID from the response
        operation_url = response.headers["Operation-Location"]
        operation_id = operation_url.split("/")[-1]

        # Poll the operation status until it's completed
        while True:
            response = requests.get(operation_url, headers=headers)
            operation_result = response.json()
            status = operation_result["status"]

            if status == "succeeded":
                # Extract the recognized texts from the result
                recognized_texts = []
                for result in operation_result["analyzeResult"]["readResults"]:
                    recognized_texts.append(result["text"])

                return recognized_texts
            elif status == "failed":
                raise Exception("Text recognition failed. Reason: " + operation_result["message"])
            else:
                time.sleep(1)
    else:
        raise Exception("Text recognition failed. Status code: " + str(response.status_code))

