# Requirement ID: FR_hybrid_1
* Description: [The system shall provide a minimum of 5 free meditation sessions that can be accessed without a premium subscription.]
* Source Persona: [Cost-Conscious Meditation User]
* Traceability: [Derived from hybrid review group H2]
* Acceptance Criteria: [Given the user is not subscribed to the premium plan, When the user browses the meditation library, Then the system shall display at least 5 unlocked free sessions accessible without payment.]
* Notes: [Rewritten from FR_auto_1 to replace vague "10 free sessions per month" with a testable minimum count grounded in H2 review evidence about paywall frustration.]
---
# Requirement ID: FR_hybrid_2
* Description: [The system shall establish a connection to the server within 5 seconds of application launch.]
* Source Persona: [Frustrated Technical User]
* Traceability: [Derived from hybrid review group H1]
* Acceptance Criteria: [Given the user opens the application on an active internet connection, When the system attempts to connect to the server, Then the connection shall be established and the home screen shall load within 5 seconds.]
* Notes: [Rewritten from FR_auto_2 to add a specific measurable time threshold. Original requirement had no acceptance criteria.]
---
# Requirement ID: FR_hybrid_3
* Description: [The system shall allow users to start meditation sessions without the application crashing.]
* Source Persona: [Frustrated Technical User]
* Traceability: [Derived from hybrid review group H1]
* Acceptance Criteria: [Given the user selects any meditation session, When the user presses the play button, Then the application shall begin playback and remain stable without crashing or force-closing.]
* Notes: [Preserved from manual pipeline FR_manual_1. Consolidated duplicate automated crash requirements into one clear requirement.]
---
# Requirement ID: FR_hybrid_4
* Description: [The system shall allow users to reach any meditation session from the home screen within three navigation interactions.]
* Source Persona: [Navigation-Frustrated User]
* Traceability: [Derived from hybrid review group H4]
* Acceptance Criteria: [Given the user is on the home screen, When the user navigates toward a specific meditation session, Then the session shall be selectable within three taps or interactions.]
* Notes: [Rewritten from FR_auto_4 which focused on response time. Navigation requirement better matches H4 review evidence. Made acceptance criteria measurable with a three-tap constraint.]
---
# Requirement ID: FR_hybrid_5
* Description: [The system shall display sleep and relaxation content within a dedicated section accessible from the main navigation.]
* Source Persona: [Sleep Improvement Seeker]
* Traceability: [Derived from hybrid review group H5]
* Acceptance Criteria: [Given the user opens the main navigation menu, When the user selects the sleep or relaxation section, Then the system shall display a list of available sleep stories and relaxation sessions.]
* Notes: [Preserved from manual pipeline FR_manual_5 with updated traceability to H5. Removed vague phrasing "easy access" and replaced with a specific navigation structure requirement.]
---
# Requirement ID: FR_hybrid_6
* Description: [The system shall maintain uninterrupted audio playback during meditation and sleep sessions, including when the device screen is locked.]
* Source Persona: [Sleep Improvement Seeker]
* Traceability: [Derived from hybrid review group H5]
* Acceptance Criteria: [Given the user starts an audio meditation or sleep session, When the user locks the device screen, Then the audio shall continue playing without interruption or stopping.]
* Notes: [Expanded from FR_manual_6 to explicitly include the screen-lock scenario, which was a commonly reported issue in H5 reviews.]
---
# Requirement ID: FR_hybrid_7
* Description: [The system shall display subscription pricing information before prompting the user to pay for premium content.]
* Source Persona: [Cost-Conscious Meditation User]
* Traceability: [Derived from hybrid review group H2]
* Acceptance Criteria: [Given the user attempts to access premium content without an active subscription, When the system detects the user is not subscribed, Then the system shall display all available subscription plan prices before any payment prompt.]
* Notes: [Rewritten from FR_auto_1 duplicate. Focused specifically on pricing transparency rather than free session count, to cover the distinct complaint about hidden costs found in H2.]
---
# Requirement ID: FR_hybrid_8
* Description: [The system shall allow users to cancel their subscription directly within the application settings.]
* Source Persona: [Dissatisfied Subscriber]
* Traceability: [Derived from hybrid review group H3]
* Acceptance Criteria: [Given the user navigates to account settings, When the user selects the subscription management option, Then the system shall provide a cancel subscription option that completes successfully and shows a confirmation message.]
* Notes: [Preserved from manual pipeline FR_manual_9 with updated traceability to H3. Added confirmation message requirement based on H3 review evidence about uncertainty after cancellation.]
---
# Requirement ID: FR_hybrid_9
* Description: [The system shall send a renewal notification to the user at least 3 days before a subscription renewal is charged.]
* Source Persona: [Dissatisfied Subscriber]
* Traceability: [Derived from hybrid review group H3]
* Acceptance Criteria: [Given a user has an active subscription set to auto-renew, When the renewal date is 3 days away, Then the system shall send a push notification or email informing the user of the upcoming charge amount and date.]
* Notes: [New requirement not present in auto pipeline. Added based on strong H3 review evidence about unexpected renewal charges. This addresses a gap the automated pipeline missed entirely.]
---
# Requirement ID: FR_hybrid_10
* Description: [The system shall provide at least one customer support contact option accessible from within the application help section.]
* Source Persona: [Dissatisfied Subscriber]
* Traceability: [Derived from hybrid review group H3]
* Acceptance Criteria: [Given the user navigates to the help or support section, When the user looks for a way to contact support, Then the system shall display at least one contact method such as a web form, email address, or live chat link.]
* Notes: [Preserved from manual pipeline FR_manual_10 with updated traceability to H3. Replaced vague "accessible" language with a specific measurable minimum of one contact method.]