/** AuthRequest */
export interface AuthRequest {
  /** Redirect Uri */
  redirect_uri: string;
}

/** AuthStatus */
export interface AuthStatus {
  /** Is Authenticated */
  is_authenticated: boolean;
  /** Username */
  username?: string | null;
  /** Email */
  email?: string | null;
}

/** CalendarEvent */
export interface CalendarEvent {
  /** Id */
  id: string;
  /** Title */
  title: string;
  /** Description */
  description?: string | null;
  /** Start Time */
  start_time: string;
  /** End Time */
  end_time: string;
  /**
   * Is All Day
   * @default false
   */
  is_all_day?: boolean;
  /**
   * Status
   * @default "confirmed"
   */
  status?: string;
  /**
   * Source
   * @default "manual"
   */
  source?: string;
  /** Meeting Request Id */
  meeting_request_id?: string | null;
}

/** EmailMessage */
export interface EmailMessage {
  /** Message Id */
  message_id: string;
  /** Sender */
  sender: string;
  /** Subject */
  subject: string;
  /** Date */
  date: string;
  /** Snippet */
  snippet: string;
  /** Contains Meeting Request */
  contains_meeting_request: boolean;
  /**
   * Detected Dates
   * @default []
   */
  detected_dates?: string[];
  /**
   * Detected Times
   * @default []
   */
  detected_times?: string[];
}

/** HTTPValidationError */
export interface HTTPValidationError {
  /** Detail */
  detail?: ValidationError[];
}

/** HealthResponse */
export interface HealthResponse {
  /** Status */
  status: string;
}

/** ScheduleRequest */
export interface ScheduleRequest {
  /** Date */
  date: string;
  /**
   * Duration Minutes
   * @default 30
   */
  duration_minutes?: number;
}

/** TimeSlot */
export interface TimeSlot {
  /** Start */
  start: string;
  /** End */
  end: string;
}

/** UserProfile */
export interface UserProfile {
  /** Name */
  name: string;
  /** Email */
  email: string;
  /** Picture */
  picture?: string | null;
}

/** ValidationError */
export interface ValidationError {
  /** Location */
  loc: (string | number)[];
  /** Message */
  msg: string;
  /** Error Type */
  type: string;
}

export type CheckHealthData = HealthResponse;

export type AuthStatusData = AuthStatus;

export type LoginData = any;

export type LoginError = HTTPValidationError;

export interface CallbackParams {
  /** Code */
  code: string;
  /** State */
  state: string;
  /** Redirect Uri */
  redirect_uri: string;
}

export type CallbackData = any;

export type CallbackError = HTTPValidationError;

export type LogoutData = any;

export type GetUserProfileData = UserProfile;

export interface ScanEmailsParams {
  /**
   * Max Results
   * @default 20
   */
  max_results?: number;
}

/** Response Scan Emails */
export type ScanEmailsData = EmailMessage[];

export type ScanEmailsError = HTTPValidationError;

/** Response Get Meeting Requests */
export type GetMeetingRequestsData = object[];

/** Response List Events */
export type ListEventsData = CalendarEvent[];

export type CreateEventData = CalendarEvent;

export type CreateEventError = HTTPValidationError;

export interface GetEventParams {
  /** Event Id */
  eventId: string;
}

export type GetEventData = CalendarEvent;

export type GetEventError = HTTPValidationError;

export interface DeleteEventParams {
  /** Event Id */
  eventId: string;
}

/** Response Delete Event */
export type DeleteEventData = object;

export type DeleteEventError = HTTPValidationError;

export interface UpdateEventParams {
  /** Event Id */
  eventId: string;
}

export type UpdateEventData = CalendarEvent;

export type UpdateEventError = HTTPValidationError;

export interface GetAvailableSlotsParams {
  /** Date */
  date: string;
  /**
   * Duration Minutes
   * @default 30
   */
  duration_minutes?: number;
}

/** Response Get Available Slots */
export type GetAvailableSlotsData = TimeSlot[];

export type GetAvailableSlotsError = HTTPValidationError;

/** Response Suggest Alternative Times */
export type SuggestAlternativeTimesData = TimeSlot[];

export type SuggestAlternativeTimesError = HTTPValidationError;
