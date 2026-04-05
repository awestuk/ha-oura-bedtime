# Oura Bedtime

A Home Assistant custom integration that displays your average bedtime over the last 10 days using the Oura Ring API.

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to Integrations > three-dot menu > Custom repositories
3. Add `awestuk/ha-oura-bedtime` as an Integration
4. Install "Oura Bedtime"
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/oura_bedtime` folder into your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings > Devices & Services > Add Integration
2. Search for "Oura Bedtime"
3. Enter your Oura Personal Access Token (create one at https://cloud.ouraring.com/personal-access-tokens)

## Sensor

The integration creates a single sensor entity:

- **Oura Ring Average Bedtime** - Your average bedtime over the last 10 days (e.g. "23:15")
  - Attribute `sample_count`: number of nights included in the average

Data is refreshed every 4 hours.
