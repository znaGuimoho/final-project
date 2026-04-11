###############################################################################################################################################################
###############################################################################################################################################################
##########################################||                                                                       ||##########################################
##########################################||   this is the more.py file where I have my about us, available houses,||##########################################
##########################################||         Renting tips, contact us FAQs Terms and conditions            ||##########################################
##########################################||                                                                       ||##########################################
###############################################################################################################################################################
###############################################################################################################################################################

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates


def more(app: FastAPI, templates: Jinja2Templates, get_db, sio):
    @app.get("/about")
    async def get_about_us(request: Request):
        return templates.TemplateResponse("more/aboutUs.html", {"request": request})

    @app.get("/renting-tips")
    async def get_about_us(request: Request):
        return templates.TemplateResponse("more/rentalTips.html", {"request": request})

    @app.get("/terms")
    async def get_terms(request: Request):
        return templates.TemplateResponse(
            "more/termsAndConditions.html", {"request": request}
        )

    @app.get("/aboutme")
    async def get_terms(request: Request):
        return templates.TemplateResponse("more/aboutMe.html", {"request": request})
