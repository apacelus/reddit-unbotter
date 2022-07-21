import logging

from platform import system
from os import path
from json import load as jload
from json import dump as jdump
from time import sleep


def get_session_cookie(username, password):
    return selenium_wrapper.get_session_cookie(username, password)


def scroll_to_next_post(post_id):
    return selenium_wrapper.scroll_to_next_post(post_id)


def join_subreddit(subreddit_id):
    pass


# vote true = up, vote false = down
def vote_post(post_id, vote):
    if vote:
        return selenium_wrapper.upvote_post(post_id)
    else:
        return selenium_wrapper.downvote_post(post_id)


def enter_comments(post_id):
    logging.info("Entering comments of post: " + post_id)
    return selenium_wrapper.enter_comments(post_id)


def leave_comment(comment_text):
    logging.info("Writing comment: " + comment_text)
    return selenium_wrapper.write_comment(comment_text)


# the main main methode
def main():
    logging.info("Starting main loop")
    # for testing:
    with open('./config/data.json', 'r') as file:
        data = jload(file)
    selenium_wrapper.login_account(data["test_acc_3432"]["session_cookie"], "test_acc_3432")

    # i = 1
    # while i < 10:
    #     print("At start: " + str(i))
    #     print("before scroll: " + str(i))
    #     i = scroll_to_next_post(i)
    #     print("after scroll: " + str(i))
    #     sleep(uniform(3, 7))
    #     if random.randint(0, 1) == 0:
    #         upvote_post(i)
    #     else:
    #         downvote_post(i)
    #     i += 1
    #     sleep(uniform(0.5, 2))
    #     print("At end: " + str(i))

    # post_id = 1
    # post_id = selenium_wrapper.scroll_to_next_post(post_id)
    # selenium_wrapper.enter_comments(post_id)
    # selenium_wrapper.write_comment("lol")

    # sleep(2)
    # print(scroll_comments(10))
    # post_id += 3
    # post_id = scroll_to_next_post(post_id)
    # enter_comments(post_id)
    # sleep(2)
    # print(scroll_comments(10))


if __name__ == "wrapper":
    logging.basicConfig(filename='./logs/unbotter.log', level=logging.INFO,
                        format='%(asctime)s |%(levelname)s| %(message)s')
    logging.info("\n\nNew log:")
    logging.info("Initializing")
    available_browsers = {
        "msedge": False,
        "chrome": False,
        "firefox": False,
        "firefox_snap": False,
        "librewolf_home": False,
        "librewolf_var": False
    }
    browser_paths_win = {
        "msedge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe"
    }
    browser_paths_linux = {
        "msedge": r"/usr/bin/microsoft-edge",
        "chrome": r"/usr/bin/google-chrome",
        "firefox": r"/usr/bin/firefox",
        "firefox_snap": r"/snap/bin/firefox",
        "librewolf_home": path.expanduser(
            '~') + r"/.local/share/flatpak/app/io.gitlab.librewolf-community/current/active/files/lib/librewolf/librewolf",
        "librewolf_var": "/var/lib/flatpak/app/io.gitlab.librewolf-community/current/active/files/lib/librewolf/librewolf"
    }
    try:
        with open('./config/settings.json', 'r') as file:
            settings_json = jload(file)
    except FileNotFoundError:
        sleep(5)
    if not path.isfile(settings_json["browser_path"]):
        logging.info("Browser path not found, checking available browsers")
        if system() == "Windows":
            logging.info("System is Windows")
            settings_json["os"] = "Windows"
            for browser_path in browser_paths_win:
                if path.isfile(browser_paths_win[browser_path]):
                    settings_json["browser_path"] = browser_paths_win[browser_path]
                    available_browsers[browser_path] = True
                    logging.info("Found " + browser_path + " in Windows")
            while True:
                try:
                    user_selected_browser = input("Please select browser. Avalable browsers: " + ", ".join(
                        key for key, value in available_browsers.items() if value) + "\n")
                    settings_json["browser_path"] = browser_paths_win[user_selected_browser]
                    settings_json["browser"] = user_selected_browser
                    break
                except KeyError:
                    print("Browser not found, check your spelling")
                    logging.info("Invalid userinput")
                    continue
        elif system() == "Linux":
            logging.info("System is Linux")
            settings_json["os"] = "Linux"
            for browser_path in browser_paths_linux:
                if path.isfile(browser_paths_linux[browser_path]):
                    settings_json["browser_path"] = browser_paths_linux[browser_path]
                    available_browsers[browser_path] = True
                    logging.info("Found " + browser_path + " in Linux")
            while True:
                try:
                    user_selected_browser = input("Please select browser. Avalable browsers: " + ", ".join(
                        key for key, value in available_browsers.items() if value) + "\n")
                    settings_json["browser_path"] = browser_paths_linux[user_selected_browser]
                    settings_json["browser"] = user_selected_browser
                    break
                except KeyError:
                    print("Browser not found, check your spelling")
                    logging.info("Invalid userinput")
                    continue
        else:
            logging.error("Unsupported os")
            print("Unsupported os")
            exit(1)
        with open("./config/settings.json", 'w') as file:
            jdump(settings_json, file)
        match settings_json["browser"]:
            case "firefox" | "firefox_snap" | "librewolf_home" | "librewolf_var":
                logging.info("Wrapper for browser: " + settings_json["browser"])
                import selenium_wrapper.firefox as selenium_wrapper
            case "chrome":
                logging.info("Wrapper for browser: Chrome(ium)")
                import selenium_wrapper.chromium as selenium_wrapper
            case "msedge":
                logging.info("Wrapper for browser: Microsoft Edge")
                import selenium_wrapper.msedge as selenium_wrapper
            case _:
                logging.error("Browser not found")
                print("Browser not found")
                exit(1)

    else:
        logging.info("Browser path verified")
        logging.info("OS: " + settings_json["os"] + ", browser: " + settings_json["browser_path"])
        match settings_json["browser"]:
            case "firefox" | "firefox_snap" | "librewolf_home" | "librewolf_var":
                logging.info("Wrapper for browser: " + settings_json["browser"])
                import selenium_wrapper.firefox as selenium_wrapper
            case "chrome":
                logging.info("Wrapper for browser: Chrome(ium)")
                import selenium_wrapper.chromium as selenium_wrapper
            case "msedge":
                logging.info("Wrapper for browser: Microsoft Edge")
                import selenium_wrapper.msedge as selenium_wrapper
            case _:
                logging.error("Browser not found")
                print("Browser not found")
                exit(1)
