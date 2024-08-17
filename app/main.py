from app.ui.gradio_ui import GradioInterface

def main():
    interface = GradioInterface()
    demo = interface.create_interface()
    demo.launch()

if __name__ == "__main__":
    main()

