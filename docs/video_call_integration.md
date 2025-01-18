# Agora Video Call Integration Guide

This guide explains how to implement video calls in your Angular application using the Agora SDK, integrated with our Django backend.

## Prerequisites

1. Install the Agora SDK in your Angular project:
```bash
npm install agora-rtc-sdk-ng
```

2. Add the following type definitions to your `tsconfig.json`:
```json
{
  "compilerOptions": {
    "types": [
      "agora-rtc-sdk-ng"
    ]
  }
}
```

## Backend API Endpoints

### 1. Generate Token
- **Endpoint**: `POST /api/v1/video-calls/token/`
- **Purpose**: Generate a token for joining a video call
- **Request Body**:
```json
{
  "doctor_id": "uuid-of-doctor",
  "slot_time": "2025-01-15T14:30:00Z"
}
```
- **Response**:
```json
{
  "token": "006...[Agora Token]",
  "channel_name": "vid_doctor-id_20250115143000",
  "uid": 12345,
  "app_id": "your-agora-app-id",
  "expiration_time": "2025-01-15T15:30:00Z",
  "role": 1
}
```

### 2. Join Video Call
- **Endpoint**: `POST /api/v1/video-calls/{call_id}/join/`
- **Purpose**: Join an existing video call
- **Response**:
```json
{
  "channel_name": "call_1234567890_1234",
  "token": "006...[Agora Token]",
  "uid": 12345,
  "expiration_time": "2025-01-15T15:30:00Z",
  "call_duration": 300,
  "app_id": "your-agora-app-id"
}
```

### 3. Refresh Token
- **Endpoint**: `POST /api/v1/video-calls/token/refresh/`
- **Purpose**: Refresh an expired token
- **Request Body**:
```json
{
  "channel_name": "existing-channel-name",
  "uid": 12345
}
```
- **Response**: Same as token generation

## Angular Implementation

### 1. Create Video Service

```typescript
// services/video.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import AgoraRTC, { IAgoraRTCClient, ICameraVideoTrack, IMicrophoneAudioTrack } from 'agora-rtc-sdk-ng';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class VideoService {
  private client: IAgoraRTCClient;
  private localAudioTrack: IMicrophoneAudioTrack;
  private localVideoTrack: ICameraVideoTrack;

  constructor(private http: HttpClient) {
    this.client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });
  }

  async generateToken(doctorId: string, slotTime: string) {
    return this.http.post('/api/v1/video-calls/token/', {
      doctor_id: doctorId,
      slot_time: slotTime
    }).toPromise();
  }

  async joinCall(callId: string) {
    const response: any = await this.http.post(
      `/api/v1/video-calls/${callId}/join/`,
      {}
    ).toPromise();

    return this.initializeAgora(response);
  }

  private async initializeAgora(callData: any) {
    try {
      // Initialize Agora client
      await this.client.join(
        callData.app_id,
        callData.channel_name,
        callData.token,
        callData.uid
      );

      // Create local audio and video tracks
      this.localAudioTrack = await AgoraRTC.createMicrophoneAudioTrack();
      this.localVideoTrack = await AgoraRTC.createCameraVideoTrack();

      // Publish tracks
      await this.client.publish([this.localAudioTrack, this.localVideoTrack]);

      // Set up remote user handling
      this.client.on('user-published', async (user, mediaType) => {
        await this.client.subscribe(user, mediaType);
        if (mediaType === 'video') {
          user.videoTrack?.play(`remote-video-${user.uid}`);
        }
        if (mediaType === 'audio') {
          user.audioTrack?.play();
        }
      });

      // Play local video
      this.localVideoTrack.play('local-video');

      return true;
    } catch (error) {
      console.error('Error joining call:', error);
      throw error;
    }
  }

  async leaveCall() {
    try {
      // Stop and close tracks
      this.localAudioTrack?.close();
      this.localVideoTrack?.close();

      // Leave the channel
      await this.client.leave();
      
      return true;
    } catch (error) {
      console.error('Error leaving call:', error);
      throw error;
    }
  }

  async toggleAudio(enabled: boolean) {
    await this.localAudioTrack?.setEnabled(enabled);
  }

  async toggleVideo(enabled: boolean) {
    await this.localVideoTrack?.setEnabled(enabled);
  }
}
```

### 2. Create Video Call Component

```typescript
// components/video-call/video-call.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { VideoService } from '../../services/video.service';

@Component({
  selector: 'app-video-call',
  template: `
    <div class="video-container">
      <div id="local-video" class="video-player"></div>
      <div id="remote-video" class="video-player"></div>
      
      <div class="controls">
        <button (click)="toggleAudio()">
          {{ isAudioEnabled ? 'Mute' : 'Unmute' }}
        </button>
        <button (click)="toggleVideo()">
          {{ isVideoEnabled ? 'Hide Video' : 'Show Video' }}
        </button>
        <button (click)="endCall()">End Call</button>
      </div>
    </div>
  `,
  styles: [`
    .video-container {
      position: relative;
      width: 100%;
      height: 100vh;
    }
    .video-player {
      width: 100%;
      height: 100%;
    }
    .controls {
      position: absolute;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      gap: 10px;
    }
  `]
})
export class VideoCallComponent implements OnInit, OnDestroy {
  isAudioEnabled = true;
  isVideoEnabled = true;
  callId: string;

  constructor(
    private videoService: VideoService,
    private route: ActivatedRoute
  ) {}

  async ngOnInit() {
    this.callId = this.route.snapshot.params['id'];
    try {
      await this.videoService.joinCall(this.callId);
    } catch (error) {
      console.error('Failed to join call:', error);
      // Handle error (show message, redirect, etc.)
    }
  }

  async toggleAudio() {
    this.isAudioEnabled = !this.isAudioEnabled;
    await this.videoService.toggleAudio(this.isAudioEnabled);
  }

  async toggleVideo() {
    this.isVideoEnabled = !this.isVideoEnabled;
    await this.videoService.toggleVideo(this.isVideoEnabled);
  }

  async endCall() {
    try {
      await this.videoService.leaveCall();
      // Navigate away or show end call screen
    } catch (error) {
      console.error('Failed to end call:', error);
    }
  }

  ngOnDestroy() {
    this.videoService.leaveCall().catch(console.error);
  }
}
```

### 3. Add to App Module

```typescript
// app.module.ts
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { VideoCallComponent } from './components/video-call/video-call.component';
import { VideoService } from './services/video.service';

@NgModule({
  declarations: [
    VideoCallComponent
  ],
  imports: [
    HttpClientModule
  ],
  providers: [
    VideoService
  ]
})
export class AppModule { }
```

## Usage Example

```typescript
// pages/appointment/appointment.component.ts
async startVideoCall() {
  try {
    const tokenData = await this.videoService.generateToken(
      this.doctorId,
      this.appointmentTime
    );
    
    // Store token data if needed
    this.router.navigate(['/video-call', tokenData.callId]);
  } catch (error) {
    console.error('Failed to start video call:', error);
  }
}
```

## Important Notes

1. **Token Expiration**: Tokens expire after 1 hour. Implement token refresh before expiration:
```typescript
const REFRESH_THRESHOLD = 5 * 60 * 1000; // 5 minutes before expiry
const expiryTime = new Date(tokenData.expiration_time).getTime();
const refreshTime = expiryTime - REFRESH_THRESHOLD;

setTimeout(async () => {
  const newToken = await this.videoService.refreshToken(
    tokenData.channel_name,
    tokenData.uid
  );
  // Update client with new token
}, refreshTime - Date.now());
```

2. **Error Handling**: Always implement proper error handling for network issues, permission denials, etc.

3. **Device Permissions**: Request camera and microphone permissions before joining:
```typescript
async checkPermissions() {
  try {
    await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    return true;
  } catch (error) {
    console.error('Permission denied:', error);
    return false;
  }
}
```

4. **Cleanup**: Always properly cleanup resources when leaving the call:
   - Close audio/video tracks
   - Leave the channel
   - Remove event listeners

5. **UI Considerations**:
   - Show loading states during connection
   - Display error messages clearly
   - Provide clear audio/video controls
   - Show connection quality indicators
   - Handle screen orientation changes

## Security Considerations

1. **Token Security**:
   - Never store tokens in localStorage
   - Refresh tokens before they expire
   - Use HTTPS for all API calls

2. **Permissions**:
   - Verify user authentication before generating tokens
   - Validate call participation rights
   - Implement proper role-based access control

3. **Privacy**:
   - Request minimum necessary permissions
   - Provide clear privacy notices
   - Implement proper data handling procedures

## Troubleshooting

Common issues and solutions:

1. **No Video/Audio**:
   - Check device permissions
   - Verify device selection
   - Check network connectivity

2. **Connection Issues**:
   - Verify token validity
   - Check network quality
   - Ensure proper initialization

3. **Performance Issues**:
   - Optimize video quality settings
   - Monitor CPU usage
   - Check network bandwidth

For more details, refer to the [Agora Web SDK Documentation](https://docs.agora.io/en/video-calling/get-started/get-started-sdk). 