from pymatrix_tests.framework.fixture import TestClassBase, testmethod
from pymatrix_tests.framework.asserts import Assert
from pymatrix_tests.integration_tests.helpers.mock_matrix_server import StaticResponseHTTPRequestHandler
import pymatrix.client
import pymatrix.specification.base
import pymatrix.specification.r0.login
import asyncio
import http
import http.server
import threading

server_hostname = "localhost"
server_port = 49993

class LoginTests(TestClassBase):

    client = None
    server = None
    worker_thread = None

    def test_method_init(self):
        self.server = http.server.HTTPServer((server_hostname, server_port), StaticResponseHTTPRequestHandler)
        self.server.timeout = 0.1 # will hang for .1 second max
        self.worker_thread = threading.Thread(target=self.server.handle_request)
        self.worker_thread.start()


        self.client = pymatrix.client.ClientFactory.get_client()
        asyncio.get_event_loop(). \
            run_until_complete(self.client.connect(server_hostname, server_port))

    def test_method_cleanup(self):
        asyncio.get_event_loop().run_until_complete(self.client.logout())
        self.worker_thread.join()
        self.server.server_close()

        # securely reset the state
        StaticResponseHTTPRequestHandler.response_body = None
        StaticResponseHTTPRequestHandler.status_code = None

    @testmethod
    def T_login_should_succeed(self):
        # arrange
        username = "local_username"
        password = "correct_password"
        response_home_server = "localhost"
        response_user_id = "@{}:{}".format(username, response_home_server)
        response_access_token = "ABCDE123456"
        response_device_id = "DEVICE123"
        response_json = "{{\"user_id\": \"{}\", \
            \"access_token\": \"{}\", \
            \"home_server\": \"{}\", \
            \"device_id\": \"{}\"}}" \
            .format(response_user_id, response_access_token,
                response_home_server, response_device_id)
        StaticResponseHTTPRequestHandler.setup_response(
            http.HTTPStatus.OK, response_json)

        # act
        response = asyncio.get_event_loop() \
            .run_until_complete(self.client.login(username, password))

        # assert
        assert isinstance(response,
            pymatrix.specification.r0.login.LoginResponseMessage)
        assert response.user_id == response_user_id
        assert response.home_server == response_home_server

    @testmethod
    def T_login_should_fail(self):
        # arrange
        username = "karthanistyr"
        password = "wrongpassword"
        errcode = "M_WRONG_PASSWORD"
        error = "Error: wrong password"
        response_json = "{{\"errcode\": \"{}\", \"error\": \"{}\"}}" \
            .format(errcode, error)
        StaticResponseHTTPRequestHandler.setup_response(
            http.HTTPStatus.FORBIDDEN, response_json)

        loop = asyncio.get_event_loop()

        # act
        response = asyncio.get_event_loop() \
            .run_until_complete(self.client.login(username, password))

        # assert
        assert isinstance(response,
            pymatrix.specification.base.ErrorMessageBase)
        assert response.error == error
        assert response.errcode == errcode
