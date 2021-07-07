"""
A Kik bot that just logs every event that it gets (new message, message read, etc.),
and echos back whatever chat messages it receives.
"""

import json
import random

import kik_unofficial.datatypes.xmpp.chatting as chatting
from kik_unofficial.client import KikClient
from kik_unofficial.callbacks import KikClientCallback
from kik_unofficial.datatypes.xmpp.errors import SignUpError, LoginError
from kik_unofficial.datatypes.xmpp.roster import FetchRosterResponse, PeerInfoResponse
from kik_unofficial.datatypes.xmpp.sign_up import RegisterResponse, UsernameUniquenessResponse
from kik_unofficial.datatypes.xmpp.login import LoginResponse, ConnectionFailedResponse

username = 'nongenericname12345'
password = 'Boatsail1!'
with open('5esrd.json', encoding="utf8") as json_file:
    rulebook = json.load(json_file)
    json_file.close()

def main():
    bot = EchoBot()


"""Menu states"""


class DeadState:
    def __init__(self):
        self.prev_input = ""

    def handle_input(self, user, parsed_user_input):
        return None


class UserCreationState:
    def __init__(self):
        self.prev_input = ""

    def handle_input(self, user, parsed_user_input):
        if parsed_user_input[0] == "y":
            with open('users.json', 'r') as userfile:
                json_users = json.load(userfile)
                json_users[user.from_jid] = {
                    "group_jid": [user.group_jid],
                    "username": [user.username],
                    "display_name": user.display_name,
                    "characters": []
                }
                userfile.close()
            with open('users.json', 'w') as userfile:
                json.dump(json_users, userfile)
            user.change_state(MainMenuState())
            return"Alright " + str(jid_to_username(user.from_jid)) + ", you're all set up!"
        elif parsed_user_input[0] == "n":
            user.state = DeadState()
            user.should_respond_to = False
            return "Ok then, fuck you bitch..."


class CharacterNamingState:
    def __init__(self):
        self.prev_input = ""

    def handle_input(self, user, parsed_user_input):
        user.change_state(CharacterNamingConfirmationState())
        user.temp_data = str(parsed_user_input)
        return "Would you like to name your character '" + \
               parsed_user_input + \
               "'? Type (y) to accept, anything else to reject, and 'cancel' to " + \
               "return to the main menu."


class CharacterNamingConfirmationState:
    def __init__(self):
        self.prev_input = ""

    def handle_input(self, user, parsed_user_input):
        if parsed_user_input[0] == 'y':
            user.change_state(MainMenuState())
            user.characters[str(user.temp_data)] = Character(str(user.temp_data))
            return "Congrats! You've got a new character."
        elif parsed_user_input[0] == 'cancel':
            user.change_state(MainMenuState())
            return "Going back to main menu."
        else:
            user.characters[user.temp_data] = Character(user.temp_data)
            user.change_state(CharacterNamingState())
            return "Suggest a different name."

    # def confirm(self):

    #     if self.state == "shouldCreate":


class CharacterSelectState:
    def __init__(self):
        self.prev_input = ""

    def handle_input(self, user, user_input):
        try:
            user.curr_characters = user.characters[user_input]
            return "You have selected: " + user_input + "."
        except:
            if len(user.characters) == 0:
                user.change_state(MainMenuState())
                return "You do not have a character, use the command 'create character.'\n Returning to main menu."
            if "cancel":
                user.change_state(MainMenuState())
                return "Returning to main menu."


class CharacterModifyState:
    def __init__(self):
        self.prev_input = ""

    def handle_input(self, user_input):
        return Character


class MainMenuState:
    def __init__(self):
        self.prev_input = ""

    def handle_input(self, user, parsed_user_input):
        if parsed_user_input[0] == "create" and parsed_user_input[1] == "character":
            user.change_state(CharacterNamingState())
            return "Feature still in development.\nWhat would you like to call the new hero?"

        elif parsed_user_input[0] == "select" and parsed_user_input[1] == "character":
            message = "Feature still in development. \n"
            if len(user.characters) == 0:
                message += "You will need to create a character first! " \
                           "Use the 'create character' command."
            else:
                message += "Please select a character. Type 'cancel' to go back to the main menu"
                for character in user.characters:
                    message += str(character.name) + "\n"
                user.change_state(CharacterSelectState())
            return message
        return None


class User:
    def __init__(self, from_jid, group_jid=None):
        if group_jid is None:
            self.group_jid = []
        else:
            self.group_jid = [group_jid]
        self.from_jid = from_jid
        self.username = ""
        self.display_name = ""
        self.curr_directory = []
        self.state = MainMenuState()
        self.should_respond_to = False
        self.characters = {}
        self.curr_character = None
        self.selected_character = None
        self.temp_data = ""

    def change_state(self, state):
        self.state = state

    def handle(self, parsed_message):
        if self.state == "in_creation":
            if parsed_message[0] == "y":
                with open('users.json', 'r') as userfile:
                    json_users = json.load(userfile)
                    json_users[self.from_jid] = {
                        "group_jid": [self.group_jid],
                        "username": [self.username]
                    }
                    userfile.close()
                with open('users.json', 'w') as userfile:
                    json.dump(json_users, userfile)
                self.state = "main_menu"
                return "Alright " + str(jid_to_username(self.from_jid)) + ", you're all set up!"
            elif parsed_message[0] == "n":
                self.state = "dead"
                self.should_respond_to = False
                return "Ok then, fuck you bitch..."
            else:
                return ""
        elif self.state == "main_menu":
            if parsed_message[0] == "current":
                return self.print_current_menu()
            elif parsed_message[0] == "goback":
                return self.step_out_of()
            else:
                try:
                    return self.step_into(parsed_message[0])
                except:
                    return "Invalid menu option. Type 'current' to get the current menu"

        else:
            return "Menu option not recognized"


    def set_username(self, new_name):
        self.username = new_name

    def get_current_menu(self):
        curr_menu = rulebook
        for directory in self.curr_directory:
            curr_menu = curr_menu[directory]
        return curr_menu

    def print_current_menu(self):
        message = "At menu "
        if len(self.curr_directory) == 0:
            message += "top"
        else:
            for directory in self.curr_directory:
                message += directory + " > "
            message = message[:-3]
        message += ":"

        for menu_item in self.get_current_menu():
            if menu_item == "content":
                for lines in menu_item:
                    message += str(lines)
                return message
            message += "  " + menu_item + "\n"
        return message
        # client.send_chat_message(self.group_jid, "")

    def get_curr_directory(self):
        return self.curr_directory

    def step_into(self, new_directory):
        self.curr_directory.append(new_directory)
        return self.print_current_menu()

    def step_out_of(self):
        self.curr_directory.pop()
        return self.print_current_menu()


class Spells:
    def __init__(self):
        self.spellcasting_ability = 0
        self.spell_save_dc = 0
        self.spell_attack_bonus = 0
        self.lvl_0_spells = []
        self.lvl_1_spells = []
        self.lvl_2_spells = []
        self.lvl_3_spells = []
        self.lvl_4_spells = []
        self.lvl_5_spells = []
        self.lvl_6_spells = []
        self.lvl_7_spells = []
        self.lvl_8_spells = []
        self.lvl_9_spells = []
        self.lvl_1_spellslots = 0
        self.lvl_2_spellslots = 0
        self.lvl_3_spellslots = 0
        self.lvl_4_spellslots = 0
        self.lvl_5_spellslots = 0
        self.lvl_6_spellslots = 0
        self.lvl_7_spellslots = 0
        self.lvl_8_spellslots = 0
        self.lvl_9_spellslots = 0


class Attack:
    def __init__(self):
        self.damage = 0
        self.additional_effect = 0


class Stats:
    def __init__(self):
        self.strength = 0
        self.dexterity = 0
        self.constitution = 0
        self.intelligence = 0
        self.wisdom = 0
        self.charisma = 0


class Skills:
    def __init__(self):
        self.acrobatics = 0
        self.animal_handling = 0
        self.arcana = 0
        self.athletics = 0
        self.deception = 0
        self.history = 0
        self.insight = 0
        self.intimidation = 0
        self.investigation = 0
        self.medicine = 0
        self.nature = 0
        self.perception = 0
        self.performance = 0
        self.persuasion = 0
        self.religion = 0
        self.sleight_of_hand = 0
        self.stealth = 0
        self.survival = 0


class Inventory:
    def __init__(self):
        self.item = ""


class Equipment:
    def __init__(self):
        self.helmet = []
        self.necklace = []
        self.ring = []
        self.chestpiece = []
        self.leggings = []
        self.shoes = []
        self.gloves = []
        self.left_hand_weapon = []
        self.right_hand_weapon = []


class Characteristics:
    def __init__(self):
        self.age = 0
        self.height = 0
        self.weight = 0
        self.eyes = 0
        self.skin = 0
        self.hair = 0
        self.appearance = ""
        self.backstory = ""
        self.additional_features_and_traits = ""
        self.allies_and_organizations = ""
        self.treasure = ""


class Character:
    def __init__(self, name):
        self.name = name
        self.dnd_class = ""
        self.race = ""
        self.background = ""
        self.alignment = ""
        self.level = ""
        self.exp = ""
        self.stats = Stats()
        self.skills = Skills()
        self.attacks_and_spellcasting = ""
        self.ac = ""
        self.initiative = ""
        self.speed = ""
        self.curr_hp = 0
        self.max_hp = 0
        self.death_saves = 0
        self.hit_dice = 0
        self.attacks = []
        self.inventory = Inventory()
        self.equipment = Equipment()
        self.feature_and_traits = ""
        self.other_proficiencies_and_languages = ""
        self.physical_characteristics = Characteristics()


class Player(Character):
    def __init__(self, name):
        super(Player, self).__init__(name)
        self.inspiration = ""
        self.personality_traits = ""
        self.ideals = ""
        self.bonds = ""
        self.flaws = ""


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class EchoBot(KikClientCallback):
    def __init__(self):
        self.client = KikClient(self, username, password)
        self.group_jid = ""
        self.from_jid = ""
        self.users = {}
        self.temp_user_jids = {}
        self.should_ignore = False
        with open('users.json') as userfile:
            json_users = json.load(userfile)
            for user in json_users.keys():
                self.users[user] = User(json_users[user], json_users[user]["group_jid"])
                self.users[user].state = ""
                self.users[user].display_name = json_users[user]["display name"]
                self.users[user].characters = json_users[user]["characters"]
            userfile.close()

    def get_rulebook(self, section):
        message = ""
        if section[1] == "classes":
            with open('02 classes.json') as json_file:
                data = json.load(json_file)
                if len(section) > 2:
                    try:
                        for item in data[section[2]]["Class Features"][section[3]]["content"]:
                            message += item + "\n"
                        self.client.send_chat_message(self.group_jid, message)
                        return
                    except:
                        self.client.send_chat_message(self.group_jid, "Class not found.")
                        return
                all_classes = data.keys()
                self.client.send_chat_message(self.group_jid, "The classes are:\n" + str(all_classes))
                return
        elif section[1] == "races":
            with open('01 races.json') as json_file:
                data = json.load(json_file)
                try:
                    for race in data["Races"]:
                        if race == section[3]:
                            if race[0] == section[4]:  # traits
                                self.client.send_chat_message(self.group_jid, race[0]["content"])
                            return
                except:
                    listRaces = "The races are:\n"
                    for race in data["Races"].keys():
                        listRaces += race
                        listRaces += "\n"
                    self.client.send_chat_message(self.group_jid, listRaces)

    def roll(self, parsed_message):
        try:
            numbers_rolled = ""
            numbers = parsed_message[1].split("d")
            numbers = list(filter(None, numbers))

            if len(numbers) == 2 and is_int(numbers[0]):
                for i in range(0, int(numbers[0])):
                    numbers_rolled += str(random.randint(1, int(numbers[1])))
                    numbers_rolled += " "
                numbers_rolled = numbers_rolled[:-1]
            else:
                numbers_rolled = str(random.randint(1, int(numbers[0])))
            self.client.send_chat_message(self.group_jid, "You rolled: \"" + numbers_rolled + "\"")
        except:
            self.client.send_chat_message(self.group_jid,
                                          "Invalid format. Second word must consist of the letter d followed by the "
                                          "number you wish to roll (ex. d6). Optionally, a number can be added to "
                                          "preface the letter d to specify the number of dice to roll (ex. 2d6)")


    # def create_character(self, name, chat_message: chatting.IncomingGroupChatMessage):
    #     character = Character(name)

    def on_authenticated(self):
            print("Now I'm Authenticated, let's request roster")
            self.client.request_roster()

    def on_login_ended(self, response: LoginResponse):
        print("Full name: {} {}".format(response.first_name, response.last_name))

    def on_chat_message_received(self, chat_message: chatting.IncomingChatMessage):
        print("[+] '{}' says: {}".format(chat_message.from_jid, chat_message.body))
        print("[+] Replaying.")
        self.client.send_chat_message(chat_message.from_jid, "You said \"" + chat_message.body + "\"!")

    def on_message_delivered(self, response: chatting.IncomingMessageDeliveredEvent):
        print("[+] Chat message with ID {} is delivered.".format(response.message_id))

    def on_message_read(self, response: chatting.IncomingMessageReadEvent):
        print("[+] Human has read the message with ID {}.".format(response.message_id))

    def on_group_message_received(self, chat_message: chatting.IncomingGroupChatMessage):
        print("[+] '{}' from group ID {} says: {}".format(chat_message.from_jid, chat_message.group_jid,
                                                          chat_message.body))
        if self.should_ignore:
            return
        parsed_message = chat_message.body.lower().split()
        self.group_jid = chat_message.group_jid
        if parsed_message[0] == "!dnd":
            try:
                self.temp_user_jids[str(chat_message.from_jid)].should_respond_to = \
                    not self.temp_user_jids[str(chat_message.from_jid)].should_respond_to
                curr_speaker = self.temp_user_jids[str(chat_message.from_jid)]

                if curr_speaker.should_respond_to:
                    self.client.send_chat_message(self.group_jid, "Hello, " + str(curr_speaker.display_name) + "!")
                else:
                    self.client.send_chat_message(self.group_jid,
                                                  "Goodbye, " + str(curr_speaker.display_name) + ".")
                self.should_ignore = False
            except:
                self.should_ignore = True
                self.from_jid = chat_message.from_jid
                self.group_jid = chat_message.group_jid
                self.client.add_friend(chat_message.from_jid)

        else:
            try:
                curr_speaker = self.temp_user_jids[str(chat_message.from_jid)]
                if curr_speaker.should_respond_to:
                    if parsed_message[0] == "rulebook":
                        self.get_rulebook(parsed_message)

                    elif parsed_message[0] == "commands":
                        self.client.send_chat_message(self.group_jid, "The DnD bot's commands are: \n"
                                                                      "-current\n"
                                                                      "-roll\n"
                                                                      "-select character\n"
                                                                      "-create character")
                                                                      # "-send noods")
                    elif parsed_message[0] == "roll":
                        self.roll(parsed_message)

                    # elif curr_speaker.state == "":
                    #
                    #     if parsed_message[0] == "create" and parsed_message[1] == "character":
                    #         self.client.send_chat_message(self.group_jid, "Feature still in development. \n"
                    #                                                       "What would you like to call the new hero?")
                    #         curr_speaker.state = "naming_a_character"
                    #
                    #     elif parsed_message[0] == "select" and parsed_message[1] == "character":
                    #         message = "Feature still in development. \n"
                    #         if len(curr_speaker.characters) == 0:
                    #             message += "You will need to create a character first! " \
                    #                        "Use the 'create character' command."
                    #         else:
                    #             message += "Please select a character. Type 'cancel' to go back to the main menu"
                    #             for character in curr_speaker.characters:
                    #                 message += str(character.name) + "\n"
                    #             curr_speaker.state = "selecting_a_character"
                    #         self.client.send_chat_message(self.group_jid, message)
                    #
                    # elif curr_speaker.state == "selecting_a_character":
                    #     try:
                    #         curr_speaker.characters[parsed_message[0]]
                    #     except:
                    #         if parsed_message[0] == "cancel":
                    #             curr_speaker.state = ""
                    #             self.client.send_chat_message(self.group_jid, "Returning to main menu.")
                    #
                    # elif curr_speaker.state == "naming_a_character":
                    #     curr_speaker.state = "character_name_confirm"
                    #     curr_speaker.temp_data = chat_message.body
                    #     self.client.send_chat_message(self.group_jid, "Would you like to name your character '" +
                    #                                   chat_message.body +
                    #                                   "'? Type (y) to accept, anything else to reject, and 'cancel' to "
                    #                                   "return to the main menu.")
                    #
                    # elif curr_speaker.state == "character_name_confirm":
                    #     if parsed_message[0] == 'y':
                    #         curr_speaker.state = ""
                    #         curr_speaker.characters[str(curr_speaker.temp_data)] = Character(str(curr_speaker.temp_data))
                    #         self.client.send_chat_message(self.group_jid, "Congrats! You've got a new character.")
                    #
                    #         return
                    #     elif parsed_message[0] == 'cancel':
                    #         curr_speaker.state = ""
                    #         self.client.send_chat_message(self.group_jid, "Going back to main menu.")
                    #         return
                    #     else:
                    #         curr_speaker.characters[curr_speaker.temp_data] = Character(curr_speaker.temp_data)
                    #         self.client.send_chat_message(self.group_jid, "Congratulations, you have the ")
                    #
                    # elif curr_speaker.state == "in_creation":
                    #     if parsed_message[0] == "y":
                    #         with open('users.json', 'r') as userfile:
                    #             json_users = json.load(userfile)
                    #             json_users[curr_speaker.from_jid] = {
                    #                 "group_jid": [curr_speaker.group_jid],
                    #                 "username": [curr_speaker.username]
                    #             }
                    #             userfile.close()
                    #         with open('users.json', 'w') as userfile:
                    #             json.dump(json_users, userfile)
                    #         curr_speaker.state = "main_menu"
                    #         self.client.send_chat_message(self.group_jid,
                    #                                       "Alright " + str(jid_to_username(curr_speaker.from_jid)) +
                    #                                       ", you're all set up!")
                    #     elif parsed_message[0] == "n":
                    #         curr_speaker.state = "dead"
                    #         curr_speaker.should_respond_to = False
                    #         self.client.send_chat_message(self.group_jid, "Ok then, fuck you bitch...")
                    #
                    # elif curr_speaker.state == "":
                    #     if parsed_message[0] == "current":
                    #         return curr_speaker.print_current_menu()
                    #     elif parsed_message[0] == "goback":
                    #         return curr_speaker.step_out_of()
                    #     else:
                    #         try:
                    #             return curr_speaker.step_into(parsed_message[0])
                    #         except:
                    #             self.client.send_chat_message(self.group_jid, "Invalid menu option. Type 'current' "
                    #                                                           "to get the current menu")
                    else:
                        message = curr_speaker.state.handle_input(curr_speaker, parsed_message)
                        if message is not None:
                            self.client.send_chat_message(self.group_jid, message)

            except:
                print("User not found.\n")

            # else:
            #     return "Menu option not recognized"

            # elif parsed_message[0] == "send" and parsed_message[1] == "noods":
            #     noods = ["https://memestatic1.fjcdn.com/comments/That+was+actually+the+original+_7bc489766fa8fbba7253483c3b913ece.jpg",
            #              "https://i.imgur.com/tVhp6L5.jpg"]
            #     noods[str(random.randint(0, 1))]

            # else:
                # try:
                #     curr_speaker = self.users[str(chat_message.from_jid)]
                #     if curr_speaker.should_respond_to:
                #         self.client.send_chat_message(self.group_jid, curr_speaker.handle(self.users, parsed_message))
                # except:
                #     print("User not found.\n")

    def on_is_typing_event_received(self, response: chatting.IncomingIsTypingEvent):
        print("[+] {} is now {}typing.".format(response.from_jid, "not " if not response.is_typing else ""))

    def on_group_is_typing_event_received(self, response: chatting.IncomingGroupIsTypingEvent):
        print("[+] {} is now {}typing in group {}".format(response.from_jid, "not " if not response.is_typing else "",
                                                          response.group_jid))

    def on_roster_received(self, response: FetchRosterResponse):
        print("[+] Chat partners:\n" + '\n'.join([str(member) for member in response.peers]))

    def on_friend_attribution(self, response: chatting.IncomingFriendAttribution):
        print("[+] Friend attribution request from " + response.referrer_jid)

    def on_image_received(self, image_message: chatting.IncomingImageMessage):
        print("[+] Image message was received from {}".format(image_message.from_jid))
    
    def on_peer_info_received(self, response: PeerInfoResponse):
        print("[+] Peer info: " + str(response.users))

        try:
            # curr_array = self.users[str(response.users[0].username)].temp
            self.temp_user_jids[self.from_jid] = self.users[str(response.users[0].jid)]
            # if self.users[str(response.users[0].jid)].should_respond_to:
            self.client.send_chat_message(self.group_jid, "Hello, " + str(response.users[0].display_name) + "!")
            # else:
            #     self.client.send_chat_message(self.group_jid, "Goodbye, " + str(response.users[0].display_name) + ".")
            self.should_ignore = False

        except:
            self.client.send_chat_message(self.group_jid, "Looks like we have a new user, " +
                                          response.users[0].display_name +
                                          ". Would you like to register as a user? (y/n)")
            self.users[str(response.users[0].jid)] = User(str(response.users[0].jid))
            self.temp_user_jids[str(self.from_jid)] = self.users[str(response.users[0].jid)]
            curr_user = self.users[str(response.users[0].jid)]
            curr_user.display_name = response.users[0].display_name
            curr_user.state = UserCreationState()
            curr_user.should_respond_to = True
            self.should_ignore = False

    def on_group_status_received(self, response: chatting.IncomingGroupStatus):
        print("[+] Status message in {}: {}".format(response.group_jid, response.status))

    def on_group_receipts_received(self, response: chatting.IncomingGroupReceiptsEvent):
        print("[+] Received receipts in group {}: {}".format(response.group_jid, ",".join(response.receipt_ids)))

    def on_status_message_received(self, response: chatting.IncomingStatusResponse):
        print("[+] Status message from {}: {}".format(response.from_jid, response.status))

    def on_username_uniqueness_received(self, response: UsernameUniquenessResponse):
        print("Is {} a unique username? {}".format(response.username, response.unique))

    def on_sign_up_ended(self, response: RegisterResponse):
        print("[+] Registered as " + response.kik_node)

    # Error handling

    def on_connection_failed(self, response: ConnectionFailedResponse):
        print("[-] Connection failed: " + response.message)

    def on_login_error(self, login_error: LoginError):
        if login_error.is_captcha():
            login_error.solve_captcha_wizard(self.client)

    def on_register_error(self, response: SignUpError):
        print("[-] Register error: {}".format(response.message))

def jid_to_username(jid):
    return jid.split('@')[0][0:-4]

if __name__ == '__main__':
    main()
