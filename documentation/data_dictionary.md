\# OVARY-X Data Dictionary



\## 1. Historical EHR Stream



| Field                 | Description                                                   |

| --------------------- | ------------------------------------------------------------- |

| patient\_id            | Synthetic or anonymized patient identifier                    |

| age                   | Age in years                                                  |

| bmi                   | Body mass index                                               |

| pcos\_status           | PCOS status                                                   |

| diagnosis\_history     | Previous diagnoses                                            |

| hba1c                 | HbA1c measurement, with units and source documented           |

| fasting\_glucose       | Fasting glucose measurement, with units and source documented |

| testosterone          | Testosterone measurement, with units and source documented    |

| lh                    | Luteinizing hormone measurement                               |

| fsh                   | Follicle-stimulating hormone measurement                      |

| genetic\_risk\_score    | Synthetic or source-supported marker, clearly labelled        |

| medication\_status     | Medication information                                        |

| previous\_cycle\_length | Previous cycle length in days                                 |



\## 2. Dynamic Wearable Stream



| Field          | Description                                   |

| -------------- | --------------------------------------------- |

| patient\_id     | Identifier matching the EHR stream            |

| timestamp      | Date and time of observation                  |

| heart\_rate     | Heart rate                                    |

| hrv            | Heart-rate variability                        |

| glucose        | Glucose measurement, if available             |

| sleep\_duration | Sleep duration                                |

| sleep\_stage    | Sleep stage or documented category            |

| steps          | Step count                                    |

| activity\_level | Activity category or measure                  |

| stress\_score   | Measured or simulated score, clearly labelled |

| cycle\_day      | Cycle day, if available                       |

| symptom\_score  | Documented or simulated score                 |



\## Data Rules



\* Use consistent patient identifiers across streams.

\* Record units, source, and missing values.

\* Never label synthetic measurements as real patient observations.

\* Do not assume every field is available in the chosen open dataset.

\* Document simulated variables and the method used to generate them.



