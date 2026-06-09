# Daily Control Bot Example Context

This is historical example context only. Do not apply it to unrelated systems.

## System Summary

Daily Control Bot for Acme Corp:

- sends scheduled notifications to Scrum team members;
- receives daily reports using predefined fields;
- validates missing reports;
- detects repeated topics three times consecutively;
- alerts possible blockers or stagnation;
- publishes reports in a Microsoft Teams channel visible to the group.

## Previously Used C1 Actors And Systems

- Integrante Scrum
- Scrum Master
- Equipo Scrum
- Daily Control Bot
- Microsoft Teams
- Microsoft Entra ID
- Microsoft Graph API

## Previously Used C2 Containers

- Teams App / Bot
- Backend API
- Scheduler
- Daily Reports Database

Important correction: C2 must preserve the consumption users from C1. Do not remove `Integrante Scrum`, `Scrum Master`, or `Equipo Scrum` unless the user asks.

## Previously Used C3 Backend API Components

- Report Controller
- Configuration Controller
- Report Service
- Daily Validation Service
- Blockage Detection Service
- Notification Service
- Teams Graph Client
- Report Repository
