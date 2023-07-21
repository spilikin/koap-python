from enum import Enum
from pydantic import BaseModel
from typing import Optional, Mapping, Any
from zeep.helpers import serialize_object


class CardTypeEnum(str, Enum):
    EGK = "EGK"
    HBA_QSIG = "HBA-qSig"
    HBA = "HBA"
    SMC_B = "SMC-B"
    HSM_B = "HSM-B"
    SMC_KT = "SMC-KT"
    KVK = "KVK"
    ZOD_20 = "ZOD_2.0"
    UNKNOWN = "UNKNOWN"
    HBAx = "HBAx"
    SM_B = "SM-B"


CARD_TYPES_SMCB = [
    CardTypeEnum.SMC_B,
    CardTypeEnum.HSM_B,
    CardTypeEnum.SM_B
]


class Card(BaseModel):
    CardType: CardTypeEnum | str
    CardHandle: str
    CardHolderName: str
    Kvnr: Optional[str]
    raw: Optional[Mapping[str, Any]]


def obj_to_card(zeep_obj) -> Card:
    card_dict = serialize_object(zeep_obj)
    card = Card.parse_obj(card_dict)
    card.raw = card_dict
    return card


class CryptEnum(str, Enum):
    RSA = "RSA"
    ECC = "ECC"


class CertRefEnum(str, Enum):
    C_AUT = "C.AUT"
    C_ENC = "C.ENC"
    C_SIG = "C.SIG"
    C_QES = "C.QES"
