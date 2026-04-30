#!/bin/bash
# Quick Test Script for KeaBuilder AI Chat Agent

echo "=== KeaBuilder AI Chat Agent Test Script ==="
echo ""

# Wait for server to start
echo "Waiting 2 seconds for server to be ready..."
sleep 2

# Test 1: Health check
echo "1. Testing health endpoint..."
curl -s -X GET http://127.0.0.1:8000/ | jq .
echo ""

# Test 2: Chat - Lead Qualification
echo "2. Testing chat - lead qualification intent..."
curl -s -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "priya@growthflow.com",
    "user_name": "Priya",
    "message": "We need to launch a conversion funnel in 4 weeks"
  }' | jq .
echo ""

# Test 3: Chat - Demo Request
echo "3. Testing chat - demo request intent..."
curl -s -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "amit@startup.com",
    "user_name": "Amit",
    "message": "Can you show me how the platform works with a demo?"
  }' | jq .
echo ""

# Test 4: Chat - Pricing Inquiry
echo "4. Testing chat - pricing inquiry intent..."
curl -s -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "sarah@company.com",
    "user_name": "Sarah",
    "message": "What are your pricing plans?"
  }' | jq .
echo ""

# Test 5: Form Processing
echo "5. Testing traditional lead form processing..."
curl -s -X POST http://127.0.0.1:8000/leads/process \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@company.com",
    "phone": "+1-555-1234",
    "budget": "We have a 50k budget",
    "timeline": "Need to launch this month",
    "goals": "Create lead capture funnels",
    "message": "Looking for urgent implementation"
  }' | jq .
echo ""

echo "=== All tests completed ==="
