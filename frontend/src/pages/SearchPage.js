import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  TextField,
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Box,
  CircularProgress,
} from '@mui/material';
import axios from 'axios';

function SearchPage() {
  const [query, setQuery] = useState('');
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/search', {
        query: query,
      });
      setCandidates(response.data.candidates);
    } catch (error) {
      console.error('Error searching candidates:', error);
      // TODO: Add error handling UI
    } finally {
      setLoading(false);
    }
  };

  const handleCandidateClick = (candidateId) => {
    navigate(`/candidate/${candidateId}`);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Find Your Next Talent
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Use natural language to describe the candidate you're looking for
        </Typography>
      </Box>

      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={10}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="e.g., Find senior Gen-AI engineers with LangChain + RAG experience in Europe, open to contract work"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="contained"
              size="large"
              onClick={handleSearch}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Search'}
            </Button>
          </Grid>
        </Grid>
      </Box>

      <Grid container spacing={3}>
        {candidates.map((candidate) => (
          <Grid item xs={12} md={6} key={candidate.id}>
            <Card
              sx={{
                cursor: 'pointer',
                '&:hover': {
                  boxShadow: 6,
                },
              }}
              onClick={() => handleCandidateClick(candidate.id)}
            >
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {candidate.name}
                </Typography>
                <Typography color="text.secondary" gutterBottom>
                  {candidate.location}
                </Typography>
                <Box sx={{ mt: 2 }}>
                  {candidate.skills.map((skill, index) => (
                    <Chip
                      key={index}
                      label={skill}
                      size="small"
                      sx={{ mr: 1, mb: 1 }}
                    />
                  ))}
                </Box>
                <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Match Score:
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{ ml: 1, color: 'primary.main', fontWeight: 'bold' }}
                  >
                    {Math.round(candidate.score)}%
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}

export default SearchPage; 