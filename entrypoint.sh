#!/bin/bash

uvicorn core.main:app --proxy-headers --host 0.0.0.0 --port 8080