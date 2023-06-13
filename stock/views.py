import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, APIKey

ALPHA_VANTAGE_API_KEY = 'X86NOH6II01P7R24'
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        # Get signup data from request body
        name = request.POST.get('name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        # Validate and create a new user
        user = User(name=name, last_name=last_name, email=email)
        user.save()

        # Generate and save API key for the user
        api_key = APIKey(user=user, key=generate_api_key())
        api_key.save()

        return JsonResponse({'api_key': api_key.key}, status=201)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def generate_api_key():
    # Implement your own logic to generate a unique API key
    # This is just a simple example, not suitable for production
    import uuid
    return str(uuid.uuid4())

def get_stock_info(request, symbol):
    # Check if the API key is provided in the request header
    api_key = request.headers.get('X-API-Key')

    # Validate the API key
    try:
        api_key_obj = APIKey.objects.get(key=api_key)
        user = api_key_obj.user
    except APIKey.DoesNotExist:
        return JsonResponse({'error': 'Invalid API key'}, status=401)

    # Make the API call to Alpha Vantage
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=compact&apikey={ALPHA_VANTAGE_API_KEY}'
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the stock market information from the Alpha Vantage response
        data = response.json()
        time_series = data['Time Series (Daily)']

        latest_date = max(time_series.keys())
        previous_date = sorted(time_series.keys())[-2]

        open_price = float(time_series[latest_date]['1. open'])
        high_price = float(time_series[latest_date]['2. high'])
        low_price = float(time_series[latest_date]['3. low'])
        previous_close = float(time_series[previous_date]['4. close'])
        latest_close = float(time_series[latest_date]['4. close'])

        variation = latest_close - previous_close

        stock_info = {
            'symbol': symbol,
            'open_price': open_price,
            'high_price': high_price,
            'low_price': low_price,
            'variation': variation
        }

        return JsonResponse(stock_info, status=200)

    return JsonResponse({'error': 'Failed to retrieve stock information'}, status=500)