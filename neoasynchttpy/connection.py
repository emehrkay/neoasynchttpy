import aiohttp
import datetime
import json
import logging

from .error import NeoAsyncHTTPyException
from .utils import Timer


logger = logging.getLogger(__name__)


class Request:

    def __init__(self, uri, statements):
        self.uri = uri
        self.statements = statements
        self.date = datetime.datetime.now().timestamp()


class Response:

    def __init__(self, request: Request):
        self.response = None
        self.text = None
        self._json = None
        self.request = request
        self.time = None

    @property
    def status(self) -> int:
        return self.response.status

    @property
    def json(self) -> dict:
        if not self._json:
            self._json = json.loads(self.text) if self.text else {}

        return self._json

    @property
    def results(self) -> list:
        return self.json.get('results', {})

    @property
    def errors(self) -> list:
        return self.json.get('errors')


class Connection:

    def __init__(self, url: str='127.0.0.1', protocol: str='http',
                 port: int=7474, username: str=None, password: str=None,
                 loop = None):
        self.url = url
        self.protocol = protocol
        self.port = port
        self.username = username
        self.password = password
        self.loop = loop
        self.commit_uri = None

        self.reset()

    def reset(self):
        self.statements = []

        return self

    @property
    def uri(self) -> str:
        return '{protocol}://{url}:{port}/db/data/transaction/commit'.format(
            protocol=self.protocol, url=self.url, port=self.port)

    @property
    def transaction_uri(self) -> str:
        return '{protocol}://{url}:{port}/db/data/transaction'.format(
            protocol=self.protocol, url=self.url, port=self.port)

    @property
    def session_kwargs(self) -> dict:
        kwargs = {}

        if self.username and self.password:
            auth = aiohttp.BasicAuth(login=self.username,
                password=self.password)
            kwargs['auth'] = auth

        if self.loop:
            kwargs['loop'] = self.loop

        return kwargs

    def statement(self, statement: str, parameters: dict=None,
        stats: bool=False):
        part = {
            'statement': statement,
        }

        if parameters:
            part['parameters'] = parameters

        if stats:
            part['includeStats'] = True

        self.statements.append(part)

        return self

    async def query(self, start_transaction: bool=False,
                    commit_transaction: bool=False,
                    rollback_transaction: bool=False) -> Response:
        statements = {
            'statements': self.statements,
        }

        if start_transaction:
            request_uri = self.transaction_uri
        elif commit_transaction or rollback_transaction:
            if not self.commit_uri:
                raise NeoAsyncHTTPyException('No open transaction to close')

            request_uri = self.commit_uri

            if rollback_transaction:
                def action(session):
                    return session.delete(request_uri)
        else:
            request_uri = self.uri

        def action(session):
            return session.post(request_uri, json=statements)

        request = Request(uri=request_uri, statements=statements)
        response = Response(request=request)

        logger.debug('Executing statements:')
        logger.debug(statements)

        with Timer() as timer:
            try:
                sk = self.session_kwargs

                async with aiohttp.ClientSession(**sk) as session:
                    async with action(session) as resp:
                        response.response = resp
                        response.text = await resp.text()

                        if start_transaction:
                            self.commit_uri = response.json.get('commit')

                        if response.errors and self.commit_uri:
                            self.commit_uri = None
            except Exception as e:
                logging.error(e, exc_info=True)

                class Resp:
                    status: 500

                response.response = Resp()
                response.errors = [e,]
                self.commit_uri = None
            finally:
                self.reset()

                if commit_transaction or rollback_transaction:
                    self.commit_uri = None

        logger.debug('runtime: {} milliseconds\n'.format(timer.elapsed))

        response.time = timer.elapsed

        return response

    async def commit(self):
        return await self.query(commit_transaction=True)

    async def rollback(self):
        return await self.query(rollback_transaction=True)
