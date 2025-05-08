from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests, time
from collections import deque
from icecream import ic as debug

WINDOW_SIZE = 10
number_store = deque(maxlen=WINDOW_SIZE)
seen_numbers = set()

AUTH_HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzQ2Njg2MjI1LCJpYXQiOjE3NDY2ODU5MjUsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6IjVhYmZiZDJjLTA5YzUtNGU4ZC05YzllLTZiMjE1MjMwZGRhNyIsInN1YiI6Iml0c3Zpc2hhbGhhY2tAZ21haWwuY29tIn0sImVtYWlsIjoiaXRzdmlzaGFsaGFja0BnbWFpbC5jb20iLCJuYW1lIjoidmlzaGFsIGd1cHRhIiwicm9sbE5vIjoiMjEwNDkyMDEwMDExOCIsImFjY2Vzc0NvZGUiOiJiYXFoV2MiLCJjbGllbnRJRCI6IjVhYmZiZDJjLTA5YzUtNGU4ZC05YzllLTZiMjE1MjMwZGRhNyIsImNsaWVudFNlY3JldCI6IlRzdWJkQ1VmQVB5elZGclYifQ.icB6TloLhE61O6WyKmQeA6tobbs4zOtMLbocx22qJNI"
}


class NumberAPIView(APIView):
    VALID_IDS = {
        'p': 'http://20.244.56.144/evaluation-service/primes',
        'f': 'http://20.244.56.144/evaluation-service/fibo',
        'e': 'http://20.244.56.144/evaluation-service/even',
        'r': 'http://20.244.56.144/evaluation-service/rand',
    }

    def get(self, request, number_id):
        if number_id not in self.VALID_IDS:
            return Response({"error": "Invalid number ID"}, status=status.HTTP_400_BAD_REQUEST)

        api_url = self.VALID_IDS[number_id]
        prev_state = list(number_store)

        try:
            start_time = time.time()
            response = requests.get(api_url, headers=AUTH_HEADERS, timeout=0.5)


            if response.status_code != 200 or (time.time() - start_time) * 1000 > 500:
                raise Exception("Slow or invalid response")

            fetched = response.json().get("numbers", [])
            debug(fetched)
            new_numbers = [n for n in fetched if n not in seen_numbers]

            for num in new_numbers:
                if len(number_store) >= WINDOW_SIZE:
                    removed = number_store.popleft()
                    seen_numbers.discard(removed)
                number_store.append(num)
                seen_numbers.add(num)

            curr_state = list(number_store)
            avg = round(sum(curr_state) / len(curr_state), 2) if curr_state else 0.0

            return Response({
                "windowPrevState": prev_state,
                "windowCurrState": curr_state,
                "numbers": new_numbers,
                "avg": avg
            })

        except Exception as e:
            debug("Exception...", e)
            curr_state = list(number_store)
            avg = round(sum(curr_state) / len(curr_state), 2) if curr_state else 0.0
            return Response({
                "windowPrevState": prev_state,
                "windowCurrState": curr_state,
                "numbers": [],
                "avg": avg
            })
