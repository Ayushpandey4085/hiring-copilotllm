import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Box,
  Button,
  CircularProgress,
  Divider,
  Link,
} from '@mui/material';
import axios from 'axios';

function CandidatePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchCandidate = useCallback(async () => {
    try {
      const response = await axios.get(`http://localhost:8000/candidate/${id}`);
      setCandidate(response.data);
    } catch (error) {
      console.error('Error fetching candidate:', error);
      // TODO: Add error handling UI
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchCandidate();
  }, [fetchCandidate]);

  const handleStartScreening = async () => {
    try {
      const response = await axios.post(`http://localhost:8000/candidate/${id}/screen`);
      navigate(`/screening/${response.data.screening_id}`);
    } catch (error) {
      console.error('Error starting screening:', error);
      // TODO: Add error handling UI
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

  if (!candidate) {
    return (
      <Container>
        <Typography variant="h5" color="error">
          Candidate not found
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {candidate.name}
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          {candidate.location}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Skills & Expertise
              </Typography>
              <Box sx={{ mb: 3 }}>
                {candidate.skills.map((skill, index) => (
                  <Chip
                    key={index}
                    label={skill}
                    sx={{ mr: 1, mb: 1 }}
                  />
                ))}
              </Box>

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" gutterBottom>
                Experience
              </Typography>
              <Typography variant="body1" paragraph>
                {candidate.experience}
              </Typography>

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" gutterBottom>
                Education
              </Typography>
              {candidate.education.map((edu, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <Typography variant="subtitle1">
                    {edu.degree}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {edu.institution} • {edu.year}
                  </Typography>
                </Box>
              ))}

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" gutterBottom>
                Contact Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Email
                  </Typography>
                  <Typography variant="body1">
                    {candidate.email}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Phone
                  </Typography>
                  <Typography variant="body1">
                    {candidate.phone}
                  </Typography>
                </Grid>
              </Grid>

              <Box sx={{ mt: 3 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Links
                </Typography>
                <Grid container spacing={2}>
                  {candidate.linkedin_url && (
                    <Grid item>
                      <Link href={candidate.linkedin_url} target="_blank" rel="noopener">
                        LinkedIn
                      </Link>
                    </Grid>
                  )}
                  {candidate.github_url && (
                    <Grid item>
                      <Link href={candidate.github_url} target="_blank" rel="noopener">
                        GitHub
                      </Link>
                    </Grid>
                  )}
                  {candidate.resume_url && (
                    <Grid item>
                      <Link href={candidate.resume_url} target="_blank" rel="noopener">
                        Resume
                      </Link>
                    </Grid>
                  )}
                </Grid>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Match Score
              </Typography>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mb: 3,
                }}
              >
                <Typography
                  variant="h3"
                  color="primary"
                  sx={{ fontWeight: 'bold' }}
                >
                  {Math.round(candidate.score)}%
                </Typography>
              </Box>

              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={handleStartScreening}
              >
                Start Screening
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}

export default CandidatePage; 