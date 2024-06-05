import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request,  Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from SupportBot import customer_support  # Assuming blog_writer is in a module named BlogAgent


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

company = "."
url = "."
file="."
file_loc="."

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@app.get("/chatbot", response_class=HTMLResponse)
async def chat_bot(request: Request):
    return templates.TemplateResponse("chatbot.html", {"request": request})

# Allow CORS for local development (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/submit")
async def handle_form_submission(companyName: str = Form(...), companyLink: str = Form(...), fileType: str = Form(...), fileInput: UploadFile = File(...)):
    global company,url,file,file_loc
    company = companyName
    url = companyLink
    file = fileType
    # Define the base directory
    base_dir = Path("C:/Users/Sarthak/Desktop/AI Agents/CustomerSupport/docs")
    
    # Ensure the directory exists
    base_dir.mkdir(parents=True, exist_ok=True)

    # Construct the full file path, ensuring filename is treated as string
    file_location = base_dir / str(fileInput.filename)
    
    # Read and write the file content
    contents = await fileInput.read()  # This reads the file content into memory
    
    try:
        with open(file_location, "wb") as f:
            f.write(contents)
        print(f"File saved at {file_location}")
    except Exception as e:
        print(f"Failed to save file: {e}")

    file_loc = file_location
    '''
    with open(file_location, "wb") as file:
        file.write(contents)
        '''

class UserInput(BaseModel):
    msg: str

@app.post("/process")
async def process_input(input_data: UserInput):
    try:
        # Log the received data
        print(f"Received data: {input_data.msg}")

        # Assume process_query is a function that processes the user's message and returns a response
        chatbot_response = customer_support(input_data.msg,company,url,file_loc)

        # Return JSON response
        return JSONResponse(content={"response": chatbot_response})
    except Exception as e:
        # Log the exception for debugging
        print(f"Error: {str(e)}")
        return JSONResponse(content={"response": "Internal Server Error"}, status_code=500)
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
