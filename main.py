import logging
from fastapi import FastAPI, HTTPException, Request,  Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from SupportBot import customer_support  # Assuming blog_writer is in a module named BlogAgent

# Initialize logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


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
'''
class ProcessRequest(BaseModel):
    #Query: str
    company_name: str
    company_link: str
'''

'''
@app.post("/submit")
async def handle_form_submission(companyName: str = Form(...), companyLink: str = Form(...), fileType: str = Form(...), fileInput: UploadFile = File(...)):
    # Process the text fields
    print(f"Company Name: {companyName}")
    print(f"Company Link: {companyLink}")
    print(f"File Type: {fileType}")

    # Read the file (if needed)
    contents = await fileInput.read()  # This will read the file content into memory
    print(f"Received file with size: {len(contents)} bytes")

    # You might want to save the file or process it in some way
    # For example, saving the file:
    file_location = f"some_directory/{fileInput.filename}"
    with open(file_location, "wb") as file:
        file.write(contents)

    return {"message": "Data received and file saved!"}
'''
'''
@app.post("/process") 
async def process_input(request: ProcessRequest):
    #Query = request.Query
    company = request.company_name
    url = request.company_link

    print(f"company:{company},url:{url}")
    #logging.info(f"Received Query: {Query}")
     
    try:
        # Call the blog_writer function
        processed_text = customer_support(company,url)
        logging.info(f"Processed text: {processed_text}")
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    return {"processed_text": processed_text}
'''
class UserInput(BaseModel):
    msg: str

@app.post("/process")
async def process_input(input_data: UserInput):
    try:
        # Log the received data
        print(f"Received data: {input_data.msg}")

        # Assume process_query is a function that processes the user's message and returns a response
        chatbot_response = customer_support(input_data.msg)

        # Return JSON response
        return JSONResponse(content={"response": chatbot_response})
    except Exception as e:
        # Log the exception for debugging
        print(f"Error: {str(e)}")
        return JSONResponse(content={"response": "Internal Server Error"}, status_code=500)
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
