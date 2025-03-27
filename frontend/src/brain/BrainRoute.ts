import {
  AuthRequest,
  AuthStatusData,
  CalendarEvent,
  CallbackData,
  CheckHealthData,
  CreateEventData,
  DeleteEventData,
  GetAvailableSlotsData,
  GetEventData,
  GetMeetingRequestsData,
  GetUserProfileData,
  ListEventsData,
  LoginData,
  LogoutData,
  ScanEmailsData,
  ScheduleRequest,
  SuggestAlternativeTimesData,
  UpdateEventData,
} from "./data-contracts";

export namespace Brain {
  /**
   * @description Check health of application. Returns 200 when OK, 500 when not.
   * @name check_health
   * @summary Check Health
   * @request GET:/_healthz
   */
  export namespace check_health {
    export type RequestParams = {};
    export type RequestQuery = {};
    export type RequestBody = never;
    export type RequestHeaders = {};
    export type ResponseBody = CheckHealthData;
  }

  /**
   * @description Check the current authentication status.
   * @tags dbtn/module:gmail_auth
   * @name auth_status
   * @summary Auth Status
   * @request GET:/routes/auth/gmail/status
   */
  export namespace auth_status {
    export type RequestParams = {};
    export type RequestQuery = {};
    export type RequestBody = never;
    export type RequestHeaders = {};
    export type ResponseBody = AuthStatusData;
  }

  /**
   * @description Initiate the OAuth flow.
   * @tags dbtn/module:gmail_auth
   * @name login
   * @summary Login
   * @request POST:/routes/auth/gmail/login
   */
  export namespace login {
    export type RequestParams = {};
    export type RequestQuery = {};
    export type RequestBody = AuthRequest;
    export type RequestHeaders = {};
    export type ResponseBody = LoginData;
  }

  /**
   * @description Handle the OAuth callback.
   * @tags dbtn/module:gmail_auth
   * @name callback
   * @summary Callback
   * @request GET:/routes/auth/gmail/callback
   */
  export namespace callback {
    export type RequestParams = {};
    export type RequestQuery = {
      /** Code */
      code: string;
      /** State */
      state: string;
      /** Redirect Uri */
      redirect_uri: string;
    };
    export type RequestBody = never;
    export type RequestHeaders = {};
    export type ResponseBody = CallbackData;
  }

  /**
   * @description Log out by removing the stored credentials.
   * @tags dbtn/module:gmail_auth
   * @name logout
   * @summary Logout
   * @request GET:/routes/auth/gmail/logout
   */
  export namespace logout {
    export type RequestParams = {};
    export type RequestQuery = {};
    export type RequestBody = never;
    export type RequestHeaders = {};
    export type ResponseBody = LogoutData;
  }

  /**
   * @description Get the authenticated user's profile information.
   * @tags dbtn/module:gmail_auth
   * @name get_user_profile
   * @summary Get User Profile
   * @request GET:/routes/auth/gmail/user
   */
  export namespace get_user_profile {
    export type RequestParams = {};
    export type RequestQuery = {};
    export type RequestBody = never;
    export type RequestHeaders = {};
    export type ResponseBody = GetUserProfileData;
  }

  /**
   * @description Scan recent emails for potential meeting requests.
   * @tags dbtn/module:gmail_scanner
   * @name scan_emails
   * @summary Scan Emails
   * @request GET:/routes/gmail/scan
   */
  export namespace scan_emails {
    export type RequestParams = {};
    export type RequestQuery = {
      /**
       * Max Results
       * @default 20
       */
      max_results?: number;
    };
    export type RequestBody = never;
    export type RequestHeaders = {};
    export type ResponseBody = ScanEmailsData;
  }

  /**
   * @description Get stored meeting requests.
   * @tags dbtn/module:gmail_scanner
   * @name get_meeting_requests
   * @summary Get Meeting Requests
   * @request GET:/routes/gmail/meeting-requests
   */
  export namespace get_meeting_requests {
    export type RequestParams = {};
    export type RequestQuery = {};
    export type RequestBody = never;
    export type RequestHeaders = {};
    export type ResponseBody = GetMeetingRequestsData;
  }

  /**
   * @description Get all calendar events
   * @tags dbtn/module:scheduler
   * @name list_events
   * @summary List Events
   * @request GET:/routes/calendar/events
   */
  export namespace list_events {
    export type RequestParams = {};
    export type RequestQuery = {};
    export type RequestBody = never;
    export type RequestHeaders = {};
    export type ResponseBody = ListEventsData;
  }

  /**
   * @description Create a new calendar event
   * @tags dbtn/module:scheduler
   * @name create_event
   * @summary Create Event
   * @request POST:/routes/calendar/events
   */
  export namespace create_event {
    export type RequestParams = {};
    export type RequestQuery = {};
    export type RequestBody = CalendarEvent;
    export type RequestHeaders = {};
    export type ResponseBody = CreateEventData;
  }

  /**
   * @description Get a specific calendar event
   * @tags dbtn/module:scheduler
   * @name get_event
   * @summary Get Event
   * @request GET:/routes/calendar/events/{event_id}
   */
  export namespace get_event {
    export type RequestParams = {
      /** Event Id */
      eventId: string;
    };
    export type RequestQuery = {};
    export type RequestBody = never;
    export type RequestHeaders = {};
    export type ResponseBody = GetEventData;
  }

  /**
   * @description Delete a calendar event
   * @tags dbtn/module:scheduler
   * @name delete_event
   * @summary Delete Event
   * @request DELETE:/routes/calendar/events/{event_id}
   */
  export namespace delete_event {
    export type RequestParams = {
      /** Event Id */
      eventId: string;
    };
    export type RequestQuery = {};
    export type RequestBody = never;
    export type RequestHeaders = {};
    export type ResponseBody = DeleteEventData;
  }

  /**
   * @description Update a calendar event
   * @tags dbtn/module:scheduler
   * @name update_event
   * @summary Update Event
   * @request PUT:/routes/calendar/events/{event_id}
   */
  export namespace update_event {
    export type RequestParams = {
      /** Event Id */
      eventId: string;
    };
    export type RequestQuery = {};
    export type RequestBody = CalendarEvent;
    export type RequestHeaders = {};
    export type ResponseBody = UpdateEventData;
  }

  /**
   * @description Find available time slots on a given day
   * @tags dbtn/module:scheduler
   * @name get_available_slots
   * @summary Get Available Slots
   * @request GET:/routes/calendar/available-slots
   */
  export namespace get_available_slots {
    export type RequestParams = {};
    export type RequestQuery = {
      /** Date */
      date: string;
      /**
       * Duration Minutes
       * @default 30
       */
      duration_minutes?: number;
    };
    export type RequestBody = never;
    export type RequestHeaders = {};
    export type ResponseBody = GetAvailableSlotsData;
  }

  /**
   * @description Suggest alternative meeting times if requested slot is not available
   * @tags dbtn/module:scheduler
   * @name suggest_alternative_times
   * @summary Suggest Alternative Times
   * @request POST:/routes/calendar/suggest-alternatives
   */
  export namespace suggest_alternative_times {
    export type RequestParams = {};
    export type RequestQuery = {};
    export type RequestBody = ScheduleRequest;
    export type RequestHeaders = {};
    export type ResponseBody = SuggestAlternativeTimesData;
  }
}
