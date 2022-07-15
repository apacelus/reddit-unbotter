import logging
from hashlib import md5
from json import load as jload
from json import dump as jdump
from os import path, mkdir


def init_new_accounts():
    import wrapper
    logging.info("Comparing accounts")
    # read accounts.txt and parse it
    with open("./config/accounts.txt", "r") as f:
        accounts_file = f.readlines()
        del accounts_file[0]
        del accounts_file[0]
        for x in range(len(accounts_file)):
            try:
                accounts_file.remove("")
            except ValueError:
                pass
            accounts_file[x] = accounts_file[x].replace("\n", "")
    with open('./config/data.json', 'r') as f:
        data_json = jload(f)
    # check if username and passwd match and exist
    to_be_added = []
    for x in range(len(accounts_file)):
        try:
            if not data_json[accounts_file[x][:accounts_file[x].find(":")]]["password"] == accounts_file[x][
                                                                                           accounts_file[x].find(
                                                                                               ":") + 1:]:
                to_be_added.append(accounts_file[x])
        except KeyError:
            to_be_added.append(accounts_file[x])
    logging.info("accounts to be added: " + str(to_be_added))
    # adding new accounts:
    for string in to_be_added:
        temp_account_dict = {
            "password": string[string.find(":") + 1:],
        }
        data_json[string[:string.find(":")]] = temp_account_dict
    with open('./config/data.json', 'w') as f:
        jdump(data_json, f)
    #######################################################
    # RANDOMIZATION/TOR ROUTING NEEDED HERE!!!!!!!!!!!!!  #
    #######################################################
    for string in to_be_added:
        print("Retrieving login cookie for: " + string[:string.find(":")])
        new_session_cookie = wrapper.get_session_cookie(string[:string.find(":")], string[string.find(":") + 1:])


if __name__ == "__main__":
    if not path.isdir("./logs"):
        logging.info("Creating log directory")
        mkdir("./logs")
    logging.basicConfig(filename='./logs/unbotter.log', level=logging.DEBUG,
                        format='%(asctime)s |%(levelname)s| %(message)s')
    if not path.isdir("./config"):
        logging.info("Creating config directory")
        mkdir("./config")
    try:
        with open('./config/data.json', 'r') as file:
            settings_json = jload(file)
    except FileNotFoundError:
        logging.info("data.json not found, creating new")
        print("data.json not found, restoring default")
        with open('./config/data.json', 'w') as file:
            with open("./default_config/data.json", "r") as template:
                file.write(template.read())
    try:
        with open("./config/accounts.txt", "r") as f:
            accounts_amount = len(f.readlines()) - 2
    except FileNotFoundError:
        logging.info("accounts.txt not found, creating new")
        print("accounts.txt not found, restoring default")
        with open('./config/accounts.txt', 'w') as file:
            with open("./default_config/accounts.txt", "r") as template:
                file.write(template.read())
        with open("./config/accounts.txt", "r") as file:
            accounts_amount = len(file.readlines()) - 2
    logging.debug("accounts_amount: " + str(accounts_amount))
    if accounts_amount <= 0:
        logging.info("No accounts found, exiting")
        print('No accounts found! Please fill in at least one account in "/config/accounts.txt"')
        exit(1)
    else:
        # Read the settings.json file
        try:
            with open('./config/settings.json', 'r') as file:
                settings_json = jload(file)
        except FileNotFoundError:
            logging.info("settings.json not found, creating new")
            print("settings.json not found, restoring default")
            with open('./config/settings.json', 'w') as file:
                with open("./default_config/settings.json", "r") as template:
                    file.write(template.read())
            with open('./config/settings.json', 'r') as file:
                settings_json = jload(file)
        # Check whether the accounts file has changed
        with open("./config/accounts.txt", 'r') as file_to_check:
            new_md5sum_of_accounts = md5(file_to_check.read().encode()).hexdigest()
            logging.info("New md5sum: " + new_md5sum_of_accounts)
            if not new_md5sum_of_accounts == settings_json["md5sum_of_accounts"]:
                logging.info("Found new accounts")
                settings_json["md5sum_of_accounts"] = new_md5sum_of_accounts
                with open('./config/settings.json', 'w') as f:
                    jdump(settings_json, f)
                init_new_accounts()
    import wrapper
