import tempfile
from uuid import uuid4
from pathlib import Path
import logging

from werkzeug.datastructures import FileStorage
from flask import Blueprint, Response
from flask_restful import Resource, Api, reqparse

from .lib import make_record

BLUEPRINT = Blueprint('premiser', __name__)


BLUEPRINT.config = {}


API = Api(BLUEPRINT)

log = logging.getLogger(__name__)


def output_html(data, code, headers=None):
    # https://github.com/flask-restful/flask-restful/issues/124
    resp = Response(data, mimetype='text/html', headers=headers)
    resp.status_code = code
    return resp


# RPC-like
class MakeQREMIS(Resource):
    def get(self):
        resp = """<html>
    <body>
        <h1>
        Create a qremis metadata record for a file.
        </h1>
        <form action=""
        enctype="multipart/form-data" method="post">
        <p>
        Please specify a file:<br>
        <input type="file" name="file" size="40">
        </p>
        <p>
        originalName:<br>
        <input type="text" name="originalName" size="30">
        </p>
        <p>
        File md5 (optional):<br>
        <input type="text" name="md5" size="30">
        </p>
        <div>
        <input type="submit" value="Submit">
        </div>
        </form>
    </body>
</html>
"""
        return output_html(resp, 200)

    def post(self):
        log.info("POST received")
        log.debug("Parsing arguments")
        parser = reqparse.RequestParser()
        parser.add_argument(
            "file",
            help="Specify the qremis file",
            type=FileStorage,
            location='files',
            required=True
        )
        parser.add_argument(
            "originalName",
            help="Specify the original name of the file as a safely encoded " +
            "string",
            type=str,
            default=None
        )
        parser.add_argument(
            "md5",
            help="Specify an md5 checksum to confirm the integrity of the " +
            "file transfer, if desired.",
            type=str,
            default=None
        )
        args = parser.parse_args()
        log.debug("Arguments parsed")

        log.debug("Creating a temporary directory to work in.")
        tmpdir = tempfile.TemporaryDirectory()
        tmp_file_path = str(Path(tmpdir.name, uuid4().hex))

        log.debug("Saving file into tmpdir")
        args['file'].save(tmp_file_path)

        log.debug("Creating qremis...")
        rec = make_record(tmp_file_path, originalName=args['originalName'])
        log.debug("qremis created")

        # Cleanup
        log.debug("Cleaning up tmpdir")
        del tmpdir

        return rec.to_dict()


@BLUEPRINT.record
def handle_configs(setup_state):
    app = setup_state.app
    BLUEPRINT.config.update(app.config)
    if BLUEPRINT.config.get("TEMPDIR"):
        tempfile.tempdir = BLUEPRINT.config['TEMPDIR']
    if BLUEPRINT.config.get("VERBOSITY"):
        logging.basicConfig(level=BLUEPRINT.config['VERBOSITY'])
    else:
        logging.basicConfig(level="WARN")

API.add_resource(MakeQREMIS, "/")
