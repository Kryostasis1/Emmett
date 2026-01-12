from prompt_toolkit.widgets import SearchToolbar, TextArea
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.output.color_depth import ColorDepth
import docker
client = docker.from_env()

style = Style([
     ('left', 'bg:ansired'),
     ('top', 'fg:#00aaaa'),
     ('bottom', 'underline bold'),
 ])

def get_titlebar(): #Top title area, including Active container list
    titlebar = [
            ("fg:green", assets.app_logo),
            ("class:title", assets.app_slogan),
            ("class:title", " (Press [Ctrl-Q] to quit.)\n"),
        ]
    return titlebar

def get_active_containers(): #Active container list
    ActiveContainerList = [
        ("class:body", "Active Containers:\n")
    ]
    ContainerList = client.containers.list(filters={"label":"Emmett"})
    for x in ContainerList:
        ContainerName = x.name
        ContainerStatus = x.status
        if ContainerStatus == "running":
            ActiveContainer = (ContainerName+" - "+ContainerStatus+"\n")
            ActiveContainerList.append(("class:testing", ActiveContainer))
    if ActiveContainerList == [("class:body", "Active Containers:\n")]:
        ActiveContainerList.append(("class:left", "None"))
    return ActiveContainerList

root_container = HSplit(
    [
        # The titlebar.
        Window(
            height=15,
            content=FormattedTextControl(get_titlebar),
            align=WindowAlign.CENTER,
        ),
        Window(
            dont_extend_height=True,
            content=FormattedTextControl(get_active_containers),
            align=WindowAlign.LEFT,
            style='class:bottom',
        )
    ]
)


#Adding Key Bindings to exit app
kb = KeyBindings()
@kb.add("c-c", eager=True)
@kb.add("c-q", eager=True)
def _(event):
    """
    Pressing Ctrl-Q or Ctrl-C will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.

    Note that Ctrl-Q does not work on all terminals. Sometimes it requires
    executing `stty -ixon`.
    """
    event.app.exit()

#Create and execute the app
application = Application(
    layout=Layout(root_container),
    key_bindings=kb,
    refresh_interval=1,
    color_depth=ColorDepth.DEPTH_24_BIT,
    full_screen=True,
)
def run():
    # Run the interface. (This runs the event loop until Ctrl-Q is pressed.)
    application.run()


if __name__ == "__main__":
    run()
