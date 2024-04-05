import vector
from duit import ui
from duit.arguments.Argument import Argument
from duit.model.DataField import DataField
from duit.ui.ContainerHelper import ContainerHelper

from duit_rest.RESTEndpoint import RESTEndpoint
from duit_rest.RESTService import RESTService


class Config:
    def __init__(self):
        container_helper = ContainerHelper(self)

        with container_helper.section("User"):
            self.name = DataField("Cat") | ui.Text("Name") | RESTEndpoint()
            self.age = DataField(21) | ui.Slider("Age", limit_min=18, limit_max=99) | RESTEndpoint()

        with container_helper.section("Application"):
            self.enabled = DataField(True) | ui.Boolean("Enabled") | Argument() | RESTEndpoint()
            self.direction = DataField(vector.obj(x=2.5, y=-0.3)) | ui.Vector("Enabled") | Argument() | RESTEndpoint()


def main():
    # create initial config
    config = Config()

    # register a custom listener for the enabled flag
    config.enabled.on_changed += lambda e: print(f"Enabled: {e}")

    # start server
    server = RESTService(title="Simple Example")
    server.add_route("/config", config)
    server.run()


if __name__ == "__main__":
    main()
