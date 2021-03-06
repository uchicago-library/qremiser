from os.path import getsize
from mimetypes import guess_type
from uuid import uuid4
from hashlib import md5, sha256
from datetime import datetime
from magic import from_file

import pyqremis

from nothashes import crc32, adler32


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"


def produce_checksums(f, hashers, buf=8192):
    data = f.read(buf)
    while data:
        for x in hashers:
            x.update(data)
        data = f.read()
    return {x.name: x.hexdigest() for x in hashers}


def _detect_mime(file_path, original_name):
    magic_num = from_file(file_path, mime=True)
    guess = None
    if original_name is not None:
        guess = guess_type(original_name)[0]
    return magic_num, guess


def make_record(file_path, objectIdentifier=None, originalName=None):
    if objectIdentifier is None:
        objectIdentifier = pyqremis.ObjectIdentifier(
            objectIdentifierType='uuid',
            objectIdentifierValue=uuid4().hex
        )

    objectCharacteristics = _build_objectCharacteristics(file_path, originalName)
    obj = pyqremis.Object(objectIdentifier, objectCharacteristics, objectCategory="file")
    if originalName is not None:
        obj.set_originalName(originalName)
    eventIdentifier = pyqremis.EventIdentifier(
        eventIdentifierType="uuid",
        eventIdentifierValue=uuid4().hex
    )
    event = pyqremis.Event(
        eventIdentifier=eventIdentifier,
        eventType="description",
        eventDateTime=datetime.now().isoformat(),
        eventOutcomeInformation=pyqremis.EventOutcomeInformation(
            eventOutcome="success"
        ),
        eventDetailInformation=pyqremis.EventDetailInformation(
            eventDetail="Initial qremis record created"
        )
    )

    relationship = pyqremis.Relationship(
        pyqremis.RelationshipIdentifier(
            relationshipIdentifierType="uuid",
            relationshipIdentifierValue=uuid4().hex
        ),
        relationshipType="link",
        relationshipSubType="simple"
    )

    relationship.add_linkingObjectIdentifier(
        pyqremis.LinkingObjectIdentifier(
            linkingObjectIdentifierType=obj.get_objectIdentifier()[0].get_objectIdentifierType(),
            linkingObjectIdentifierValue=obj.get_objectIdentifier()[0].get_objectIdentifierValue()
        )
    )

    relationship.add_linkingEventIdentifier(
        pyqremis.LinkingEventIdentifier(
            linkingEventIdentifierType=event.get_eventIdentifier()[0].get_eventIdentifierType(),
            linkingEventIdentifierValue=event.get_eventIdentifier()[0].get_eventIdentifierValue()
        )
    )

    relationship.add_relationshipNote(
        "Link between object and original description event"
    )

    qremis = pyqremis.Qremis(obj, event, relationship)
    return qremis


def _build_objectCharacteristics(file_path, originalName):
    fixitys = _build_fixitys(file_path)
    size = str(getsize(file_path))
    formats = _build_formats(file_path, originalName)
    return pyqremis.ObjectCharacteristics(
        *fixitys,
        *formats,
        size=size,
    )


def _build_fixitys(file_path):
    hashers = [md5(), sha256(), crc32(), adler32()]
    with open(file_path, 'rb') as f:
        checksums = produce_checksums(f, hashers)
    return [pyqremis.Fixity(messageDigestAlgorithm=x, messageDigest=checksums[x]) for x in checksums
            if checksums[x] != 'None']


def _build_formats(file_path, originalName):
    formats = []
    x = _detect_mime(file_path, originalName)
    if x[0] is not None:
        formats.append(
            pyqremis.Format(
                pyqremis.FormatDesignation(
                    formatName=x[0]
                ),
                formatNote="From magic number (python3 magic.from_file)"
            )
        )

    if x[1] is not None:
        formats.append(
            pyqremis.Format(
                pyqremis.FormatDesignation(
                    formatName=x[1]
                ),
                formatNote="From file extension (python3 mimetypes.guess_type)"
            )
        )

    return formats
