import os
import pathlib
import json
from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware

def get_router_config() -> dict:
    try:
        cfg = json.loads(open("routers.json").read())
    except:
        return {"routers": {}}
    return cfg

def is_auth_disabled(router_config: dict, name: str) -> bool:
    return router_config.get("routers", {}).get(name, {}).get("disableAuth", True)

def import_api_routers() -> APIRouter:
    """Create top level router including all user defined endpoints."""
    routes = APIRouter(prefix="/routes")

    router_config = get_router_config()
    src_path = pathlib.Path(__file__).parent
    apis_path = src_path / "app" / "apis"

    api_names = [
        p.relative_to(apis_path).parent.as_posix()
        for p in apis_path.glob("*/__init__.py")
    ]

    api_module_prefix = "app.apis."

    for name in api_names:
        print(f"Importing API: {name}")
        try:
            api_module = __import__(api_module_prefix + name, fromlist=[name])
            api_router = getattr(api_module, "router", None)
            if isinstance(api_router, APIRouter):
                routes.include_router(api_router)
        except Exception as e:
            print(e)
            continue

    return routes

def create_app() -> FastAPI:
    """Create the app."""
    app = FastAPI()
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )
    
    app.include_router(import_api_routers())

    for route in app.routes:
        if hasattr(route, "methods"):
            for method in route.methods:
                print(f"{method} {route.path}")

    return app

app = create_app()
