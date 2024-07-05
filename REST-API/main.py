from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os
from starlette.responses import FileResponse

app = FastAPI()

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
    region_name='ap-south-1'
)

BUCKET_NAME = 'trafficapp-vid-bucket'

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        s3_client.upload_fileobj(file.file, BUCKET_NAME, file.filename)
        return JSONResponse(content={"message": "File uploaded successfully"}, status_code=200)
    except NoCredentialsError:
        raise HTTPException(status_code=400, detail="AWS credentials not found")
    except PartialCredentialsError:
        raise HTTPException(status_code=400, detail="Incomplete AWS credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get")
async def get_vid(video_filename: str = Query(...)):

    local_filename = '/tmp/' + os.path.basename(video_filename)
    s3_client.download_file(BUCKET_NAME, video_filename, local_filename)

    #TODO - Add a removeFile() method to remove the file downloaded to /tmp

    return FileResponse(local_filename, media_type='application/octet-stream', filename=os.path.basename(local_filename))


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
