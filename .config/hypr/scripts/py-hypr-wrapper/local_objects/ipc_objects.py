class LocalIPCRequest:
    def __init__(
        self,
        initiator_id: str,
        requested_action_name: str,
        requested_action_parameters: dict,
    ):
        self.initiator_id: str = initiator_id
        self.requested_action_name: str = requested_action_name
        self.requested_action_parameters: dict = requested_action_parameters

    def __repr__(self) -> str:
        return (
            f"Request<ID[{self.initiator_id}],REQUEST[{self.requested_action_name}]"
            + f",PARAMS[{str(self.requested_action_parameters)}]>"
        )


class LocalIPCResponse:
    def __init__(self, initiator_id: str, response_ok: bool, response: dict):
        self.initiator_id: str = initiator_id
        self.response_ok: bool = response_ok
        self.response: dict = response

    def __repr__(self) -> str:
        return (
            f"Response<ID[{self.initiator_id}],OK[{self.response_ok}]"
            + f",RESPONSE[{str(self.response)}]>"
        )


class WrongInitiatorId(Exception):
    def __init__(self, request: LocalIPCRequest, response: LocalIPCResponse):
        super().__init__(
            f"Mismatching initiator IDs: {request.initiator_id} and {response.initiator_id}"
        )
        self.request: LocalIPCRequest = request
        self.response: LocalIPCResponse = response


class IPCRequestFailed(Exception):
    def __init__(self, request: LocalIPCRequest, response: LocalIPCResponse):
        super().__init__(
            f"Request [{request.requested_action_name}] failed with [{response.response}]"
        )
        self.request: LocalIPCRequest = request
        self.response: LocalIPCResponse = response
