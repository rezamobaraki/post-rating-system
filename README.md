## use-cases


# mechanism of fraud detection
- not suspected : rate will save and post stats will update
(Detect and Action)

- flag and prevent: Block fraudulent activity before it occurs
- flag and repost: Identify and resubmit suspicious content for review
- flag and remove: Detect and delete fraudulent content immediately
- flag and update: Mark for later analysis and update post statistics

after this detection, it will update the post stats.

in first step in 10 min 1000 is_fraud= True ,

Pagination

"""
This module contains the FraudDetectionSystem class that is responsible for detecting fraudulent activities.

There is several approach to detect fraudulent activities:

1. Rate limiting: Limit the number of actions a user can perform within a certain period.
2. Suspicious activity detection: Detect suspicious activities based on certain thresholds.
3. User behavior analysis: Analyze user behavior to detect fraudulent activities.

Fraud Detection Mechanism:
- Analyse and remove: In this mechanism we can use a Flag on as fraudulent.
- Prevent: In this mechanism we can use a Throttled exception to prevent the user from performing the action.

"""