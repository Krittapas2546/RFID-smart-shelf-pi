🚀 Installation & Usage
Follow the steps below to run the project on your machine:

1. Clone the Repository

bash
Copy
Edit
git clone https://github.com/Krittapas2546/RFID-smart-shelf.git
cd RFID-smart-shelf
2. Create and Activate the Virtual Environment

For Windows:

bash
Copy
Edit
python -m venv venv
.\venv\Scripts\activate
For macOS/Linux:

bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies

Make sure to create a requirements.txt file using pip freeze > requirements.txt to capture all required Python libraries.

To install dependencies, use:

bash
Copy
Edit
pip install -r requirements.txt
4. Run the Backend Server

bash
Copy
Edit
python main.py  # or the main server file
5. Open the UI

Open a browser and go to http://127.0.0.1:5000 (or the port where your server is running).

Or directly open the src/templates/shelf_ui.html file.

Usage Instructions:
When new tasks arrive, they appear in the Job Queue.

If there are multiple tasks, press Select to start a task.

The UI shows the target location (red light) on the shelf.

Place the product in the correct location, and the UI will update to green.

The system automatically continues the next task in the queue.

👤 Author
Krittapas P. - (@Krittapas2546)

📄 License
This project is licensed under the MIT License.

