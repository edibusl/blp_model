import main
import file_manager

main.create_db()
file_manager.init(False)
app = main.start_flask()
