# BG Game Analysis Software  

The BG Game Analysis software is a comprehensive framework for esports performance enhancement, leveraging advanced hardware and software tools to collect, process, and analyze gameplay data.  

---

## Table of Contents  
- [Introduction](#introduction)  
- [Data Collection](#data-collection)  
- [Preprocessing and Data Management](#preprocessing-and-data-management)  
- [Analysis and Visualization](#analysis-and-visualization)  
- [Advanced Insights](#advanced-insights)  

---

## Introduction  
The BG Game Analysis software is designed to help players and coaches improve performance by providing actionable insights. By combining data from multiple hardware and software tools, the software delivers a unified dataset for in-depth analysis, offering both raw data and intuitive visualizations for a seamless user experience.  

---

## Data Collection  
The data collection process begins with the execution of the `main.bat` file, which initializes all connected devices and software. Key components include:  

- **Tobii Pro Spark Eye Tracker**: Collects precise gaze data to monitor player focus during gameplay.  
- **Logitech Stream Webcam**: Records high-resolution facial expressions for emotional and contextual insights.  
- **Keyboard and Mouse Tracking Software**: Logs user inputs to analyze movement timing and ability usage.  
- **Open Broadcaster Software (OBS)**: Records gameplay sessions and overlays relevant tracking data into VODs (Video on Demand).  

All inputs are synchronized to ensure precise timing and alignment across datasets, enabling accurate and comprehensive analysis.  

---

## Preprocessing and Data Management  
Once data is collected, it undergoes preprocessing:  

1. **Cleaning and Normalization**: Ensures raw data consistency and usability.  
2. **Data Merging**: Consolidates gaze patterns, player inputs, and other tracked metrics into a unified dataset.  
3. **Storage in SQL Server**: Provides a scalable and robust platform for efficient data storage, retrieval, and management.  

The SQL server acts as the central repository, handling large volumes of data with ease and supporting complex queries for further analysis.  

---

## Analysis and Visualization  
The merged dataset is visualized through an interactive dashboard that provides:  

- Key performance indicators (KPIs).  
- Insights on gaze patterns, player interactions, and overall performance metrics.  
- Intuitive and actionable feedback for players and analysts.  

The dashboard ensures that users can explore gameplay data in a format designed for ease of understanding and actionable improvements.  

---

## Advanced Insights  
Stored data is used to develop advanced analytical models to:  

- Evaluate player performance.  
- Identify specific areas for improvement.  
- Generate actionable recommendations through performance-enhancing tools like virtual assistants.  

This end-to-end process ensures the collected data is accurate, organized, and optimized for practical application in esports.  

---

## Conclusion  
The BG Game Analysis software combines cutting-edge technology with intuitive design to deliver unparalleled insights into gameplay performance. Whether you're a player looking to refine your skills or a coach guiding a team, this software provides the tools needed to achieve your goals.  

For more information or support, please contact the development team.  

---
