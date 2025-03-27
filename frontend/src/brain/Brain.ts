import {
  AuthRequest,
  AuthStatusData,
  CalendarEvent,
  CallbackData,
  CallbackError,
  CallbackParams,
  CheckHealthData,
  CreateEventData,
  CreateEventError,
  DeleteEventData,
  DeleteEventError,
  DeleteEventParams,
  GetAvailableSlotsData,
  GetAvailableSlotsError,
  GetAvailableSlotsParams,
  GetEventData,
  GetEventError,
  GetEventParams,
  GetMeetingRequestsData,
  GetUserProfileData,
  ListEventsData,
  LoginData,
  LoginError,
  LogoutData,
  ScanEmailsData,
  ScanEmailsError,
  ScanEmailsParams,
  ScheduleRequest,
  SuggestAlternativeTimesData,
  SuggestAlternativeTimesError,
  UpdateEventData,
  UpdateEventError,
  UpdateEventParams,
} from "./data-contracts";
import { ContentType, HttpClient, RequestParams } from "./http-client";

export class Brain<SecurityDataType = unknown> extends HttpClient<SecurityDataType> {
  /**
   * @description Check health of application. Returns 200 when OK, 500 when not.
   *
   * @name check_health
   * @summary Check Health
   * @request GET:/_healthz
   */
  check_health = (params: RequestParams = {}) =>
    this.request<CheckHealthData, any>({
      path: `/_healthz`,
      method: "GET",
      ...params,
    });

  /**
   * @description Check the current authentication status.
   *
   * @tags dbtn/module:gmail_auth
   * @name auth_status
   * @summary Auth Status
   * @request GET:/routes/auth/gmail/status
   */
  auth_status = (params: RequestParams = {}) =>
    this.request<AuthStatusData, any>({
      path: `/routes/auth/gmail/status`,
      method: "GET",
      ...params,
    });

  /**
   * @description Initiate the OAuth flow.
   *
   * @tags dbtn/module:gmail_auth
   * @name login
   * @summary Login
   * @request POST:/routes/auth/gmail/login
   */
  login = (data: AuthRequest, params: RequestParams = {}) =>
    this.request<LoginData, LoginError>({
      path: `/routes/auth/gmail/login`,
      method: "POST",
      body: data,
      type: ContentType.Json,
      ...params,
    });

  /**
   * @description Handle the OAuth callback.
   *
   * @tags dbtn/module:gmail_auth
   * @name callback
   * @summary Callback
   * @request GET:/routes/auth/gmail/callback
   */
  callback = (query: CallbackParams, params: RequestParams = {}) =>
    this.request<CallbackData, CallbackError>({
      path: `/routes/auth/gmail/callback`,
      method: "GET",
      query: query,
      ...params,
    });

  /**
   * @description Log out by removing the stored credentials.
   *
   * @tags dbtn/module:gmail_auth
   * @name logout
   * @summary Logout
   * @request GET:/routes/auth/gmail/logout
   */
  logout = (params: RequestParams = {}) =>
    this.request<LogoutData, any>({
      path: `/routes/auth/gmail/logout`,
      method: "GET",
      ...params,
    });

  /**
   * @description Get the authenticated user's profile information.
   *
   * @tags dbtn/module:gmail_auth
   * @name get_user_profile
   * @summary Get User Profile
   * @request GET:/routes/auth/gmail/user
   */
  get_user_profile = (params: RequestParams = {}) =>
    this.request<GetUserProfileData, any>({
      path: `/routes/auth/gmail/user`,
      method: "GET",
      ...params,
    });

  /**
   * @description Scan recent emails for potential meeting requests.
   *
   * @tags dbtn/module:gmail_scanner
   * @name scan_emails
   * @summary Scan Emails
   * @request GET:/routes/gmail/scan
   */
  scan_emails = (query: ScanEmailsParams, params: RequestParams = {}) =>
    this.request<ScanEmailsData, ScanEmailsError>({
      path: `/routes/gmail/scan`,
      method: "GET",
      query: query,
      ...params,
    });

  /**
   * @description Get stored meeting requests.
   *
   * @tags dbtn/module:gmail_scanner
   * @name get_meeting_requests
   * @summary Get Meeting Requests
   * @request GET:/routes/gmail/meeting-requests
   */
  get_meeting_requests = (params: RequestParams = {}) =>
    this.request<GetMeetingRequestsData, any>({
      path: `/routes/gmail/meeting-requests`,
      method: "GET",
      ...params,
    });

  /**
   * @description Get all calendar events
   *
   * @tags dbtn/module:scheduler
   * @name list_events
   * @summary List Events
   * @request GET:/routes/calendar/events
   */
  list_events = (params: RequestParams = {}) =>
    this.request<ListEventsData, any>({
      path: `/routes/calendar/events`,
      method: "GET",
      ...params,
    });

  /**
   * @description Create a new calendar event
   *
   * @tags dbtn/module:scheduler
   * @name create_event
   * @summary Create Event
   * @request POST:/routes/calendar/events
   */
  create_event = (data: CalendarEvent, params: RequestParams = {}) =>
    this.request<CreateEventData, CreateEventError>({
      path: `/routes/calendar/events`,
      method: "POST",
      body: data,
      type: ContentType.Json,
      ...params,
    });

  /**
   * @description Get a specific calendar event
   *
   * @tags dbtn/module:scheduler
   * @name get_event
   * @summary Get Event
   * @request GET:/routes/calendar/events/{event_id}
   */
  get_event = ({ eventId, ...query }: GetEventParams, params: RequestParams = {}) =>
    this.request<GetEventData, GetEventError>({
      path: `/routes/calendar/events/${eventId}`,
      method: "GET",
      ...params,
    });

  /**
   * @description Delete a calendar event
   *
   * @tags dbtn/module:scheduler
   * @name delete_event
   * @summary Delete Event
   * @request DELETE:/routes/calendar/events/{event_id}
   */
  delete_event = ({ eventId, ...query }: DeleteEventParams, params: RequestParams = {}) =>
    this.request<DeleteEventData, DeleteEventError>({
      path: `/routes/calendar/events/${eventId}`,
      method: "DELETE",
      ...params,
    });

  /**
   * @description Update a calendar event
   *
   * @tags dbtn/module:scheduler
   * @name update_event
   * @summary Update Event
   * @request PUT:/routes/calendar/events/{event_id}
   */
  update_event = ({ eventId, ...query }: UpdateEventParams, data: CalendarEvent, params: RequestParams = {}) =>
    this.request<UpdateEventData, UpdateEventError>({
      path: `/routes/calendar/events/${eventId}`,
      method: "PUT",
      body: data,
      type: ContentType.Json,
      ...params,
    });

  /**
   * @description Find available time slots on a given day
   *
   * @tags dbtn/module:scheduler
   * @name get_available_slots
   * @summary Get Available Slots
   * @request GET:/routes/calendar/available-slots
   */
  get_available_slots = (query: GetAvailableSlotsParams, params: RequestParams = {}) =>
    this.request<GetAvailableSlotsData, GetAvailableSlotsError>({
      path: `/routes/calendar/available-slots`,
      method: "GET",
      query: query,
      ...params,
    });

  /**
   * @description Suggest alternative meeting times if requested slot is not available
   *
   * @tags dbtn/module:scheduler
   * @name suggest_alternative_times
   * @summary Suggest Alternative Times
   * @request POST:/routes/calendar/suggest-alternatives
   */
  suggest_alternative_times = (data: ScheduleRequest, params: RequestParams = {}) =>
    this.request<SuggestAlternativeTimesData, SuggestAlternativeTimesError>({
      path: `/routes/calendar/suggest-alternatives`,
      method: "POST",
      body: data,
      type: ContentType.Json,
      ...params,
    });
}
