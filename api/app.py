import logging

from flask import Flask
from flask import request

from swapi import SWApi

dev_mode = True

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(asctime)s %(message)s",
)

def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index() -> dict:
        return {
            "data": "Hello, welcome to Sleuth backend interview task. Please see instructions in README.md"
        }


    @app.route("/health")
    def health_check() -> dict:
        response = SWApi().get("/")
        return {"swapi_is_healthy": response.status_code == 200, "urls": response.json()}


    @app.route("/swapi/vehicles", methods=["GET"])
    def swapi_min_cargo_capacity_vehicles() -> dict:
        """Lists vehicles with cargo capacity that is greater or equal to the provided value.

        For each vehicle list the attrs: name, model and cargo capacity
        """

        # Validate min_cargo_capacity param
        min_cargo_capacity = request.args.get("min_cargo_capacity")
        if min_cargo_capacity:
            try:
                min_cargo_capacity = int(min_cargo_capacity)
            except:
                return "Invalid Request", 400
        else:
            min_cargo_capacity = None

        # Collecting vehicles meeting condition
        vehicles = []
        params = {
            "page": 1
        }
        while True:
            try:
                response = SWApi().get("/vehicles", params)
                if response.status_code == 200:
                    data = response.json()
                    for vehicle in data["results"]:
                        cargo_capacity = None
                        try:
                            cargo_capacity = int(vehicle["cargo_capacity"])
                        except:
                            pass
                        if min_cargo_capacity is None or (cargo_capacity is not None and cargo_capacity >= min_cargo_capacity):
                            vehicles.append({
                                "name": vehicle["name"],
                                "model": vehicle["model"],
                                "cargo_capacity": vehicle["cargo_capacity"],
                            });
                    if data["next"] is None:
                        break
                    params["page"] += 1
                else:
                    return response.text, response.status_code
            except:
                return "Not Reachable", 404

        return {
            "available_vehicles": vehicles
        }

    return app

main = create_app()

if __name__ == "__main__":
    main.run(host="0.0.0.0", port=5001)
