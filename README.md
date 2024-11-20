Readme for the text to speach service running on server.

The service file is for systemctl.

The endpoints are as follows:

`GET "/voices"` -> returns the avaialable voices that can be used for TTS generation.

`GET "/languages"` -> returns the avaialable languages that can be used for TTS generation.

`POST "/text-to-speech"` body=`{text: data to read back, voice: the voice to use, rate: the speech rate, pitch: the pitch the speecher is altered}`
