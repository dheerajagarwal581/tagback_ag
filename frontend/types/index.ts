// Shared TypeScript Interfaces for QR-Based Temporary Communication Platform

export type RoomStatus = "Pending" | "Active" | "Rejected" | "Closed" | "Recovered";

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface OwnerProfile {
  display_name: string;
  profile_image_url?: string | null;
  public_bio?: string | null;
  visibility_settings: {
    show_bio: boolean;
    show_avatar: boolean;
  };
}

export interface PublicProfile {
  public_token: string;
  display_name: string;
  public_bio?: string | null;
  profile_image_url?: string | null;
  is_active: boolean;
}

export interface ItemDetails {
  item_name: string;
  description?: string | null;
  found_location?: string | null;
  photograph_url?: string | null;
  initial_message: string;
}

export interface Room {
  id: string;
  owner_id: string;
  guest_session_id: string;
  status: RoomStatus;
  created_at: string;
  updated_at: string;
  closed_at?: string | null;
  item_details?: ItemDetails;
  owner_display_name?: string;
  finder_display_name?: string;
}

export interface Message {
  id: string;
  room_id: string;
  sender_type: "owner" | "finder" | "system";
  sender_display_name: string;
  content: string;
  message_type: "text" | "image" | "location";
  media_url?: string | null;
  location_lat?: number | null;
  location_lng?: number | null;
  is_read: boolean;
  created_at: string;
}

export interface NotificationItem {
  id: string;
  owner_id: string;
  room_id: string;
  notification_type: "NEW_REQUEST" | "NEW_MESSAGE" | "ROOM_RESOLVED";
  title: string;
  content: string;
  is_read: boolean;
  created_at: string;
}

export interface ContactSubmitRequest {
  public_token: string;
  item_name: string;
  finder_display_name: string;
  initial_message: string;
  description?: string;
  found_location?: string;
  photograph_url?: string;
}

export interface ContactSubmitResponse {
  room_id: string;
  status: RoomStatus;
  recovery_token: string;
  recovery_url: string;
  created_at: string;
}
