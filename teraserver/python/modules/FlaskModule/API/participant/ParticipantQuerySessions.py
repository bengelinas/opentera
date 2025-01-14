from flask import session
from flask_restx import Resource, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import participant_multi_auth
from modules.FlaskModule.FlaskModule import participant_api_ns as api
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraSession import TeraSession
from modules.DatabaseModule.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_session', type=int, help='ID of the session to query')
get_parser.add_argument('session_uuid', type=str, help='Session UUID to query')
get_parser.add_argument('status', type=int, help='Limit to specific session status')
get_parser.add_argument('limit', type=int, help='Maximum number of results to return')
get_parser.add_argument('offset', type=int, help='Number of items to ignore in results, offset from 0-index')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')
get_parser.add_argument('status', type=int, help='Limit to specific session status')
get_parser.add_argument('start_date', type=inputs.date, help='Start date, sessions before that date will be ignored')
get_parser.add_argument('end_date', type=inputs.date, help='End date, sessions after that date will be ignored')

post_parser = api.parser()


class ParticipantQuerySessions(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @participant_multi_auth.login_required(role='full')
    @api.expect(get_parser)
    @api.doc(description='Get session associated with participant.',
             responses={200: 'Success',
                        400: 'Bad request',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        current_participant = TeraParticipant.get_participant_by_uuid(session['_user_id'])
        participant_access = DBManager.participantAccess(current_participant)

        args = get_parser.parse_args(strict=True)

        minimal = False
        if args['list']:
            minimal = True

        filters = {}
        if args['id_session']:
            filters['id_session'] = args['id_session']

        if args['session_uuid']:
            filters['session_uuid'] = args['session_uuid']

        # List comprehension, get all sessions with filter
        sessions_list = [data.to_json(minimal=minimal) for data in TeraSession.get_sessions_for_participant(
            part_id=current_participant.id_participant, status=args['status'], limit=args['limit'],
            offset=args['offset'], start_date=args['start_date'], end_date=args['end_date'], filters=filters)]
        #  participant_access.query_session(filters=filters, limit=args['limit'], offset=args['offset'],
        #                                  start_date=args['start_date'], end_date=args['end_date'])]

        return sessions_list

    @participant_multi_auth.login_required(role='full')
    @api.expect(post_parser)
    @api.doc(description='To be documented '
                         'To be documented',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def post(self):
        return gettext('Not implemented'), 501
