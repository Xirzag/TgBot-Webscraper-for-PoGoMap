import random
import threading

import telegram
import time
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Location)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import persistence
import pokedex
from login import should_be_logged, login
import pokemon_hook
import logging

# Enable logging
from persistence import user_data

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

NEAR_POK_CHOOSE, NEAR_POK_DIST, CHECK_POKEMON, SET_ALERT, SET_MAP = range(5)
default_distance = 300

used_map = 'pogoesp'


def xstr(s):
    return '?' if s is None else str(s)


@should_be_logged
def near_pok(bot, update):
    user_data(update).init('pokemon_last_distance', 300)
    user_data(update).init('last_location', pokemon_hook.def_coord)
    update.message.reply_text('Send location to see near pokemons or use /last.\n')
    return NEAR_POK_CHOOSE


def near_pok_by_location(bot, update):
    update.message.reply_text('Send distance or click /default or /last.\n')
    user_data(update)['last_location'] = update.message.location
    return NEAR_POK_DIST


def get_near_pok(bot, update):
    try:
        dist = int(update.message.text)
        user_data(update)['pokemon_last_distance'] = dist
        return get_pokemons(bot, update)
    except ValueError as verr:
        pass  # do job to handle: s does not contain anything convertible to int
    except Exception as ex:
        pass

    update.message.reply_text(update.message.text + " it's no a number.\n")
    return ConversationHandler.END


def get_default_near_pok(bot, update):
    user_data(update)['pokemon_last_distance'] = default_distance
    return get_pokemons(bot, update)


wtf_pokemon = pokedex.ids(['Porygon', 'Porygon2', 'Plusle', 'Minum', 'Unown', 'Tyranitar', 'Dragonite', 'Combusken',
                           'Swampert', 'Sceptile', 'Chansey', 'Blissey', 'Vigoroth', 'Slaking', 'Sceptile',
                           'Gardevoir', 'Swalot', 'Kirlia', 'Meganium', 'Machamp', 'Snorlax', 'Seviper', 'Togetic',
                           'Nuzleaf', 'Shiftry', 'Lunatone', 'Solrock', 'Chimecho', 'Wynaut', 'Swablu',
                           'Relicanth', 'Gorebyss', 'Huntail', 'Spinda', 'Torkoal', 'Bagon', 'Shelgon', 'Beldum',
                           'Metang', 'Lairon'])

wtf_near_pokemon = pokedex.ids(['Dratini', 'Dragonair', 'Magikarp', 'Gyarados', 'Vaporeon', 'Jolteon', 'Flareon',
                                'Omastar', 'Chikorita', 'Bulbasaur', 'Zangoose', 'Slakoth', 'Pikachu', 'Raychu',
                                'Geodude', 'Graveler', 'Golem', 'Machop', 'Machoke', 'Abra', 'Kadabra', 'Alakazam',
                                'Lapras', 'Aron'])

alert_poke = pokedex.ids(['Plusle', 'Minum', 'Unown', 'Slaking', 'Gardevoir', 'Slaking', 'Lotad', 'Sceptile', 'Seviper',
                          'Wailord', 'Lunatone', 'Solrock', 'Lairon'])

alert_near_poke = pokedex.ids(['Tyranitar', 'Dragonite', 'Combusken', 'Swampert', 'Sceptile', 'Chansey', 'Blissey',
                               'Vigoroth', 'Gyarados', 'Vaporeon', 'Meganium', 'Machamp', 'Snorlax',
                               'Togetic', 'Nuzleaf', 'Golem', 'Shiftry', 'Aron'])


def time_to_str(time_, format='%H:%M'):
    localtime = time.localtime(time_ / 1000)
    return time.strftime(format, localtime)


def pokemon_to_str(pokemon):
    pok_str = pokemon['pokemon_name'] + ' ' + str(pokemon['cp']) + '  ' + '\n' \
              + xstr(pokemon['individual_attack']) + '/' + xstr(pokemon['individual_defense']) + '/' + xstr(
        pokemon['individual_stamina']) \
              + '  ' + time_to_str(pokemon['disappear_time'])
    if pokemon_hook.is_magikarp_xl(pokemon):
        pok_str += ' XL'
    if pokemon_hook.is_rattata_xs(pokemon):
        pok_str += ' XS'
    return pok_str


@should_be_logged
def send_pokemon_with_filter(bot, update, filters):
    user_data(update).init('pokemon_last_distance', 300)
    user_data(update).init('last_location', pokemon_hook.def_coord)
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.FIND_LOCATION)
    data = user_data(update)
    coords = pokemon_hook.get_coordinates(data['last_location'], data['pokemon_last_distance'])
    data = pokemon_hook.get_cached_pokemons(pokemon_hook.maps[used_map], coords, pokemon_hook.hide_pok)

    if 'Error' in data:
        update.message.reply_text('Error reading pokemons\n' + data['Error'])
        return ConversationHandler.END

    filtered = pokemon_hook.filter_pokemon(data['pokemons'], filters)

    for pokemon in filtered:
        update.message.reply_text(pokemon_to_str(pokemon))
        update.message.reply_location(location=Location(pokemon['longitude'], pokemon['latitude']))

    if not filtered:
        update.message.reply_text('No interesting pokemon')

    return ConversationHandler.END


@should_be_logged
def get_pokemons(bot, update):
    user_data(update).init('pokemon_last_distance', 300)
    user_data(update).init('last_location', pokemon_hook.def_coord)
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.FIND_LOCATION)
    data = user_data(update)
    coords = pokemon_hook.get_coordinates(data['last_location'], data['pokemon_last_distance'])
    data = pokemon_hook.get_cached_pokemons(pokemon_hook.maps[used_map], coords, pokemon_hook.hide_pok)

    if 'Error' in data:
        update.message.reply_text('Error reading pokemons\n' + data['Error'])
        return ConversationHandler.END

    filtered = pokemon_hook.filter_pokemon(data['pokemons'], [
        pokemon_hook.select_iv_pokemons(98),
        pokemon_hook.select_iv_pokemons(90, pokedex.ids('Jynx')),
        pokemon_hook.select_specific_pokemons(wtf_pokemon),
        pokemon_hook.select_specific_pokemons(alert_poke),
        pokemon_hook.filter_near_pokemons(coords),
        pokemon_hook.select_xl_magikarp(),
        pokemon_hook.select_xs_rattata(),
        pokemon_hook.select_specific_pokemons(wtf_near_pokemon),
        pokemon_hook.select_specific_pokemons(alert_near_poke),
        pokemon_hook.select_iv_pokemons(90),
        # pokemon_hook.select_third_gen()
    ])

    for pokemon in filtered:
        update.message.reply_text(pokemon_to_str(pokemon))
        update.message.reply_location(location=Location(pokemon['longitude'], pokemon['latitude']))

    if not filtered:
        update.message.reply_text('No interesting pokemon')

    return ConversationHandler.END


@should_be_logged
def get_medal_pokemons(bot, update):
    user_data(update).init('pokemon_last_distance', 300)
    user_data(update).init('last_location', pokemon_hook.def_coord)
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.FIND_LOCATION)
    data = user_data(update)
    coords = pokemon_hook.get_coordinates(data['last_location'], data['pokemon_last_distance'])
    data = pokemon_hook.get_cached_pokemons(pokemon_hook.maps[used_map], coords, pokemon_hook.hide_pok)

    if 'Error' in data:
        update.message.reply_text('Error reading pokemons\n' + data['Error'])
        return ConversationHandler.END

    filtered = pokemon_hook.filter_pokemon(data['pokemons'], [
        pokemon_hook.select_xl_magikarp(),
        pokemon_hook.select_xs_rattata(),
        pokemon_hook.select_specific_pokemons(pokedex.ids(['Pikachu'])),
    ])

    for pokemon in filtered:
        update.message.reply_text(pokemon_to_str(pokemon))
        update.message.reply_location(location=Location(pokemon['longitude'], pokemon['latitude']))

    if not filtered:
        update.message.reply_text('No interesting pokemon')

    return ConversationHandler.END


@should_be_logged
def get_rattata_xs(bot, update):
    user_data(update).init('pokemon_last_distance', 300)
    user_data(update).init('last_location', pokemon_hook.def_coord)
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.FIND_LOCATION)
    data = user_data(update)
    coords = pokemon_hook.get_coordinates(data['last_location'], data['pokemon_last_distance'])
    data = pokemon_hook.get_cached_pokemons(pokemon_hook.maps[used_map], coords, pokemon_hook.hide_pok)

    if 'Error' in data:
        update.message.reply_text('Error reading pokemons\n' + data['Error'])
        return ConversationHandler.END

    filtered = pokemon_hook.filter_pokemon(data['pokemons'], [
        pokemon_hook.select_xs_rattata(),
    ])

    for pokemon in filtered:
        update.message.reply_text(pokemon_to_str(pokemon))
        update.message.reply_location(location=Location(pokemon['longitude'], pokemon['latitude']))

    if not filtered:
        update.message.reply_text('No interesting pokemon')

    return ConversationHandler.END


def alert_users_from_pokemons(bot):
    try:
        for user_id in persistence.get_saved_ids():
            data = user_data(user_id)
            data.init('poke_alert', 'NO ALERT')
            if data['logged'] == 'LOGGED' and data['poke_alert'] != 'NO ALERT' and 'chat' in data:
                alert_pokemons(bot, user_id)
    except Exception as e:
        pass

    threading.Timer(60 * random.randint(14, 22) - random.randint(0, 60), lambda: alert_users_from_pokemons(bot)).start()


def alert_pokemons(bot, user_id):
    data = user_data(user_id)

    data.init('pokemon_last_distance', 300)
    data.init('last_location', pokemon_hook.def_coord)

    coords = pokemon_hook.get_coordinates(data['last_location'], data['pokemon_last_distance'] * 2.0)
    poke_data = pokemon_hook.get_cached_pokemons(pokemon_hook.maps[used_map], coords,
                                                 pokemon_hook.hide_pok)

    if 'Error' in poke_data:
        bot.send_message(chat_id=data['chat'], text='ERROR IN ALERTS\n' + poke_data['Error'])
        return

    filters = {
        'ALERT': [
            pokemon_hook.select_iv_pokemons(90, pokedex.ids('Jynx')),
            pokemon_hook.select_iv_pokemons(100),
            pokemon_hook.select_specific_pokemons(alert_poke),
            pokemon_hook.filter_near_pokemons(coords),
            pokemon_hook.select_specific_pokemons(alert_near_poke)
        ],
        'NEAR': [
            pokemon_hook.select_specific_pokemons(pokedex.ids(['Unown'])),
            pokemon_hook.select_iv_pokemons(90, pokedex.ids('Jynx')),
            pokemon_hook.filter_near_pokemons(coords),
            pokemon_hook.select_iv_pokemons(100),
            pokemon_hook.select_specific_pokemons(alert_poke),
            pokemon_hook.select_specific_pokemons(alert_near_poke)
        ],
        'UNOWN': [
            pokemon_hook.select_iv_pokemons(90, pokedex.ids('Jynx')),
            pokemon_hook.select_specific_pokemons(pokedex.ids(['Unown'])),
        ]
    }

    filtered = pokemon_hook.filter_pokemon(poke_data['pokemons'], filters[data['poke_alert']])

    if filtered:
        bot.send_message(chat_id=data['chat'], text='*POKEMON ALERTS*', parse_mode=telegram.ParseMode.MARKDOWN)

    for pokemon in filtered:
        bot.send_message(chat_id=data['chat'], text=pokemon_to_str(pokemon))
        bot.send_location(chat_id=data['chat'], latitude=pokemon['latitude'], longitude=pokemon['longitude'])


@should_be_logged
def get_gyms_by_user(bot, update):
    parts = update.message.text.split(' ')
    if len(parts) == 1:
        update.message.reply_text('Send user name after the command')
        return ConversationHandler.END

    user_name = parts[1]

    data = user_data(update)
    coords = pokemon_hook.get_coordinates(data['last_location'], 1000.0)
    poke_data = pokemon_hook.get_cached_pokemons(pokemon_hook.maps[used_map], coords,
                                                 pokemon_hook.hide_pok)

    if 'Error' in poke_data:
        update.message.reply_text('Error reading gyms\n' + poke_data['Error'])
        return ConversationHandler.END

    have_gyms = False

    for id, gym in poke_data['gyms'].items():
        for pokemon in gym['pokemon']:
            if pokemon['trainer_name'].lower() == user_name.lower():
                have_gyms = True
                update.message.reply_text(gym['name'] + ': ' + pokemon['pokemon_name'] + '  CP:'
                                          + str(pokemon['cp_decayed']) + '/' + str(pokemon['pokemon_cp'])
                                          + '\nSince ' + time_to_str(pokemon['deployment_time'], '%d/%m %H:%M'))
                update.message.reply_location(location=Location(gym['longitude'], gym['latitude']))
                break

    if not have_gyms:
        update.message.reply_text(user_name + ' don\'t have gyms')

    return ConversationHandler.END


@should_be_logged
def set_alert(bot, update):
    data = user_data(update)
    data.init('poke_alert', 'NO ALERT')
    custom_keyboard = [['alert', 'no alert', 'unown'],
                       ['alert near only', 'cancel']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=data['chat'],
                     text="Current mode " + data['poke_alert'] + " Select a option",
                     reply_markup=reply_markup)

    return SET_ALERT


def save_alert_mode(bot, update):
    data = user_data(update)
    reply_markup = telegram.ReplyKeyboardRemove()
    options = {'alert': 'ALERT', 'no alert': 'NO ALERT', 'alert near only': 'NEAR', 'unown': 'UNOWN'}
    text = update.message.text

    if text == 'cancel' or text not in options:
        bot.send_message(chat_id=data['chat'],
                         text='Canceled',
                         reply_markup=reply_markup)
        return ConversationHandler.END

    data['poke_alert'] = options[text]
    bot.send_message(chat_id=data['chat'],
                     text='Saved ' + update.message.text,
                     reply_markup=reply_markup)

    return ConversationHandler.END


@should_be_logged
def cancel(bot, update):
    update.message.reply_text('Cancel.\n')
    return ConversationHandler.END


@should_be_logged
def update_location_dialog(bot, update):
    user_data(update)['last_location'] = update.message.location
    update.message.reply_text('Location updated. /getnear')


@should_be_logged
def set_map(bot, update):
    data = user_data(update)
    custom_keyboard = [[x] for x in pokemon_hook.maps.keys()]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=data['chat'],
                     text="Current map " + used_map + " Select a option",
                     reply_markup=reply_markup)

    return SET_MAP


def save_map(bot, update):
    global used_map
    text = update.message.text

    if text == 'cancel' or text not in pokemon_hook.maps.keys():
        update.message.reply_text('Canceled', reply_markup=telegram.ReplyKeyboardRemove())
        return ConversationHandler.END

    used_map = update.message.text
    update.message.reply_text('Saved ' + update.message.text, reply_markup=telegram.ReplyKeyboardRemove())

    return ConversationHandler.END


@should_be_logged
def get_pokemon(bot, update):
    parts = update.message.text.split(' ')
    if len(parts) == 1:
        update.message.reply_text('Send user name after the command')
        return ConversationHandler.END

    pokemon = parts[1]
    send_pokemon_with_filter(bot, update, [pokemon_hook.select_specific_pokemons(pokedex.ids(pokemon))])


def init(updater):
    near_pok_handler = ConversationHandler(
        entry_points=[CommandHandler('nearpok', near_pok)],

        states={
            NEAR_POK_CHOOSE: [MessageHandler(Filters.location, near_pok_by_location),
                              CommandHandler('last', get_pokemons)],
            NEAR_POK_DIST: [MessageHandler(Filters.text, get_near_pok),
                            CommandHandler('default', get_default_near_pok),
                            CommandHandler('last', get_pokemons)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    set_alert_handler = ConversationHandler(
        entry_points=[CommandHandler('setalert', set_alert)],

        states={
            SET_ALERT: [MessageHandler(Filters.text, save_alert_mode)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    set_map_handler = ConversationHandler(
        entry_points=[CommandHandler('setmap', set_map)],

        states={
            SET_MAP: [MessageHandler(Filters.text, save_map)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp = updater.dispatcher

    dp.add_handler(near_pok_handler)
    dp.add_handler(set_alert_handler)
    dp.add_handler(set_map_handler)
    dp.add_handler(CommandHandler('usergym', get_gyms_by_user))
    dp.add_handler(CommandHandler('getnear', get_pokemons))
    dp.add_handler(CommandHandler('getpokemon', get_pokemon))
    dp.add_handler(CommandHandler('getmedals', get_medal_pokemons))
    dp.add_handler(CommandHandler('getrattataxs', get_rattata_xs))
    dp.add_handler(MessageHandler(Filters.location, update_location_dialog))

    threading.Timer(10, lambda: alert_users_from_pokemons(updater.bot)).start()
