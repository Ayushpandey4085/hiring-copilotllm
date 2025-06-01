import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Box,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Alert,
} from '@mui/material';
import axios from 'axios';

function ScreeningPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [screening, setScreening] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const fetchScreening = useCallback(async () => {
    try {
      const response = await axios.get(`http://localhost:8000/screening/${id}`);
      setScreening(response.data);
      setAnswers(new Array(response.data.questions.length).fill(''));
    } catch (error) {
      console.error('Error fetching screening:', error);
      setError('Failed to load screening questions');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchScreening();
  }, [fetchScreening]);

  const handleAnswerChange = (index, value) => {
    const newAnswers = [...answers];
    newAnswers[index] = value;
    setAnswers(newAnswers);
  };

  const handleNext = () => {
    if (currentStep < screening.questions.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      await axios.post(`http://localhost:8000/screening/${id}/submit`, {
        answers: answers,
      });
      // Navigate to results or show feedback
      navigate(`/candidate/${screening.candidate_id}`);
    } catch (error) {
      console.error('Error submitting answers:', error);
      setError('Failed to submit answers');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '60vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  if (!screening) {
    return (
      <Container>
        <Typography variant="h5" color="error">
          Screening not found
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Technical Screening
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Please answer the following questions to assess your technical expertise
        </Typography>
      </Box>

      <Stepper activeStep={currentStep} sx={{ mb: 4 }}>
        {screening.questions.map((_, index) => (
          <Step key={index}>
            <StepLabel>Question {index + 1}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Question {currentStep + 1}
          </Typography>
          <Typography variant="body1" paragraph>
            {screening.questions[currentStep]}
          </Typography>

          <TextField
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            value={answers[currentStep]}
            onChange={(e) => handleAnswerChange(currentStep, e.target.value)}
            placeholder="Type your answer here..."
          />

          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
            <Button
              variant="outlined"
              onClick={handleBack}
              disabled={currentStep === 0}
            >
              Back
            </Button>
            {currentStep < screening.questions.length - 1 ? (
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={!answers[currentStep].trim()}
              >
                Next
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={handleSubmit}
                disabled={submitting || !answers.every((a) => a.trim())}
              >
                {submitting ? <CircularProgress size={24} /> : 'Submit'}
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
}

export default ScreeningPage; 