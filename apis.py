from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException
import httpx
from model_binaries_controllers import model_binaries_loader, update_model_binaries_from_document
from Models import MetaDataModel, QueryModel
from preprocessing_controllers import preprocess_document
from query_controllers import get_relevant_links
from web_scrapper_controllers import web_scrapper

router = APIRouter()

model_binaries = model_binaries_loader()

# Constants
MAX_LINKS_ON_RESPONSE = 25
THRESHOLD = 0.1
    
@router.post("/metadata")
async def get_metadata(req: MetaDataModel):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(req.url, timeout=10.0)
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.title.string.strip() if soup.title else ""
            description = ""

            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                description = meta_desc["content"].strip()

            if not description or (description==""):
                og_desc = soup.find("meta", property="og:description")
                if og_desc and og_desc.get("content"):
                    description = og_desc["content"].strip()
            
            if not description or (description==""):
                first_p = soup.find("p")
                if first_p:
                    description = first_p.get_text(strip=True)

            if not description or (description==""):
                description = "No summary available for this page."

            return {"title": title, "description": description}
    except Exception as e:
        return {"title": "Untitled", "description": "No summary available for this page.", "error": str(e)}


@router.post("/get-query-result")
def getQueryResult(query_request: QueryModel):
    try:
        status, relevant_links = get_relevant_links(
            nlp=model_binaries["NLP"],
            query=query_request.query,
            vectorizer=model_binaries["VECTORIZER"],
            vectors=model_binaries["VECTORS"],
            links=model_binaries["LINKS"],
            n=MAX_LINKS_ON_RESPONSE,
            thres=THRESHOLD,
            usr=query_request.user_role
        )

        response_message = f"Here are the top resources that I found on {query_request.query}:"

        if status == -1:
            response_message = f"Unfortunatly, I was not able to find any resources relevant to \"{query_request.query}\". Please, Try again with any relevant keywords you can think of. You can also refer the main careers site:"

        return {"response_message": response_message,
                "relevant_links": relevant_links}
    except Exception as E:
        raise HTTPException(status_code=500, detail=str(E))
    
@router.post("/update-model")
def updateBinaries(token: str):
    url_to_document = web_scrapper(root="http://careers.humber.ca")
    url_to_document = preprocess_document(url_to_document)
    update_model_binaries_from_document(url_to_document)
    return {"message":"Model's Binaries are updated successfully"}