# Prerequisites

Before beginning, ensure you have NPM and NGROK installed on your machine. All of us should already have Python installed. If not, install Python as well.

You can check whether you already have NPM installed by running the following command in your terminal:

    npm -v

If already installed, this command will return the installed version of NPM.

You can check whether you already have NGROK installed by running the following command in your terminal:

    ngrok -v

If already installed, this command will return the installed version of NGROK.

Linked below are the installation guides for both NPM and NGROK.

Node.JS and NPM: https://docs.npmjs.com/downloading-and-installing-node-js-and-npm
NGROK: https://ngrok.com/downloads/linux

To use NGROK, you are required to provide an auth token. I will share mine in the Discord server, however you can make your own if you wish. You will need to run the following command in your terminal:

    ngrok config add-authtoken <token from Discord>

# Cloning backend repo and setting up environment

#### NOTE: Many of the installation steps depending on having access to the .env files and various API keys that were used in this project. Since this is a public repo, I will provide the .env files in our private Discord server so that the internet does not bankrupt me.

Navigate to or create a directory in which you wish to download the project. In this directory, open a terminal and enter the following commands:

    git clone https://github.com/Felopater-Melika/HackMT25
    cd HackMT25

This will clone the backend's repo and navigate into that directory.

During the Hackathon, I believe many of us installed the required libraries into our global Python installs. However, that can be a bit iffy and PIP likes to throw a fit over this. So, for this guide, we will create a virtual environment for our project. To create a virtual environment, enter the following command:

    python3 -m venv pyapi
    
This will create a virtual Python installation inside of a directory titled 'pyapi'. 

#### NOTE: If you have opened the project in VSCode, the Python extension may offer to create a virtual environment for you. Don't let it. Not only will that make the rest of this guide invalid, but VSCode doesn't do it correctly.

Now, we need to install all required libraries for this project. To install the requirements: enter the following command:

    pyapi/bin/pip install -r requirements.txt

This will install all of the required libraries, including Uvicorn and FastAPI, into our virtual environment.

Finally need to provide all of the environment variables required by the project, such as the OpenAI and Twilio API keys. In the root of the project (HackMT25), create a new file titled .env. Into that file, paste the text from the Discord titled BACKEND ENV, and save the file.

# Cloning frontend repo and setting up environment

Navigate back to the directory where you cloned the backend repo using the following command:

    cd ..

This will navigate the terminal backwards in the path. Now clone the frontend repo and navigate into it using the following commands:

    git clone https://github.com/Felopater-Melika/HackMT25Front
    cd HackMT25Front

This will clone the frontend repo and navigate the terminal into its root directory.

Once inside of the HackMT25Front directory, we need to install the required NPM packages for this project, including Next and Axios. You can do this by running the following command:

    npm install

This will install all of the required packages listed in package.json.

The frontend also requires a .env at the root of the project. Even though it does not contain and sensitive information, I will still share it through the Discord server exclusively.

In the root of the project (HackMT25Front), create a new file titled .env. Into that file, paste the text from the Discord titled FRONTEND ENV, and save the file.


# Running the demo

The demo requires three separate terminals to run. One for NGROK, one for the backend server, and another for the frontend server.

## Running and setting up NGROK
Before starting the backend server, we need to provide an NGROK URL. For this example, we will have the backend run on port 8000, however if you already have a service running on port 8000, you can use any port other than port 3000. Open a new terminal and enter the following command:

    ngrok http 8000

This will start a new NGROK service on port 8000. You should see a CLI that looks like this:
                                                                                                                                 
    Session Status                online                                                                                                          
    Account                       Noah Cagle (Plan: Free)                                                                                         
    Version                       3.22.1                                                                                                          
    Region                        United States (us)                                                                                              
    Latency                       49ms                                                                                                            
    Web Interface                 http://127.0.0.1:4040                                                                                           
    Forwarding                    https://8381-2601-483-801-5af0-9dc3-8ea6-ea54-6787.ngrok-free.app -> http://localhost:8000                      
                                                                                                                                              
    Connections                   ttl     opn     rt1     rt5     p50     p90                                                                     
                                  0       0       0.00    0.00    0.00    0.00                                                                    
                                                                                                                                              
We need the URL listed as 'Forwarding'. Copy and paste it into the backend's .env file as the value of NGROK_URL. It should look like this:

    NGROK_URL=https://8381-2601-483-801-5af0-9dc3-8ea6-ea54-6787.ngrok-free.app

Save the .env and keep NGROK running. That URL is where Twilio will send all of its requests, so it needs to remain live. If you have to restart NGROK for any reason, make sure to update the NGROK_URL value in .env.

In the backend's .env file, change the value of PATIENT_PHONE_NUMBER to your phone number. It is currently set to mine as an example. Make sure to include the country code. It should look like this:

    PATIENT_PHONE_NUMBER=+13174206969

Save the .env file.

## Running the backend server
Navigate into the HackMT25 directory, and run the following command:

    pyapi/bin/uvicorn main:app --reload --port 8000

This will launch the backend server on port 8000. If you had to use a different port for NGROK, use that port instead. NGROK and the backend server need to run on the same port in order for them to work together.

## Running the frontend server
Navigate into the HackMT25Front directory and run the following command:

    npm run dev

This will launch the frontend's NodeJS server. You should see a link to the server in the CLI's output, which will look like this:

      ▲ Next.js 15.1.6 (Turbopack)
      - Local:        http://localhost:3000
      - Network:      http://192.168.0.14:3000
      - Environments: .env

Open your web browser and navigate to the following URL:

    http://localhost:3000/signup

The page will auto-generate fake patient data. Click the 'Register' button at the bottom of the form.

#### NOTE: If you had to use a different port for the backend server and NGROK that wasn't port 8000, you'll need to find src/app/signup/page.tsx and update all calls to 'localhost:8000' to point to the correct port.

Now navigate to the Dashboard at the following URL:


    http://localhost:3000/dashboard/1

The /1 is the patientId of the example patient you created on the sign up page. You should see that information in a card at the top-left of the page, with the Make a Call button.

Pressing the Make a Call button will reach out to the back-end server your started earlier, which will reach out to Twilio to place a phone call to the PATIENT_PHONE_NUMBER value you updated earlier.

#### NOTE: If you had to use a different port for the backend server and NGROK that wasn't port 8000, you'll need to find src/app/dashboard/[slug]/page.tsx and update all calls to 'localhost:8000' to point to the correct port.

Yay! You did it!

# Final Note

### This demo will not work forever. It depends on the validity of my Twilio API key and my OpenAI API key, both of which have a limit amount of funds. If you ever want to use this demo in the distant future, you will need to create your own Twilio and OpenAI keys and update them in the backend's .env file.
