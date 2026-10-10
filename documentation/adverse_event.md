\# Adverse Event Definition



\## Prediction Horizon



Two hours after the current observation.



\## Prediction Target



Predict whether the patient will enter a predefined elevated metabolic-risk state within the next two hours.



\## Target Column



adverse\_event\_2h



\## Target Encoding



1 = The predefined event occurs within the next two hours.

0 = The predefined event does not occur within the next two hours.



\## Implementation Requirement



The physiological measurement, event threshold, and labelling rule must be selected and documented before model training. The threshold must be supported by the selected dataset or an appropriate reference. Do not invent a clinical threshold or tune it merely to improve model results.



\## Limitation



This is a research prediction, not a validated medical warning or diagnosis.



