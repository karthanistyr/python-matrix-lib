from enum import Enum
import pymatrix.constants as consts

class LocaleStringEnum(Enum):
    French = "fr"
    English = "en"

    def from_string(locale_string):
        candidate = [loc for loc in LocaleStringEnum \
            if loc.value == locale_string]

        if(not any(candidate)):
            raise ValueError("Can't find the specified locale.")
        return candidate[0]

class Localisation:
    _locale = LocaleStringEnum.English
    def set_locale(locale: LocaleStringEnum):
        Localisation._locale = locale

    def get_message(message_key):
        return strings[Localisation._locale][message_key]

strings = {
    LocaleStringEnum.French: {
        consts.ErrorStringEnum.NoLoginProvided: "Aucun identifiant n'a été "
        "spécifié. Vous devez spécifier au moins une des options suivantes: "
        "identifiant Matrix, identifiant tiers (3PID) ou jeton d'API.",
        consts.ErrorStringEnum.MalformedMessage: "Message malformé.",
        consts.ErrorStringEnum.NotInSpecification: "Message non présent "
        "dans la spécification."
        },
    LocaleStringEnum.English: {
        consts.ErrorStringEnum.NoLoginProvided: "No login identifier was "
        "specified. You must specify at least one of the following options: "
            "Matrix identifier, third-party identifier (3PID) or API token.",
        consts.ErrorStringEnum.MalformedMessage: "Malformed message.",
        consts.ErrorStringEnum.NotInSpecification: "Message not present "
        "in the specification."
        }
    }
