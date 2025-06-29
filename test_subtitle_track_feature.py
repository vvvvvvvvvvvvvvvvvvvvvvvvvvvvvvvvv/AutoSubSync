import unittest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock, call
import sys

# Add the main directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'main'))

from main.functions.subtitle_track_selector import (
    get_subtitle_tracks,
    extract_subtitle_track,
    get_best_subtitle_track
)
from main.functions.enhanced_alass_integration import (
    extract_best_subtitle_for_alass,
    run_alass_with_subtitle_track,
    cleanup_extracted_subtitle
)

class TestSubtitleTrackSelector(unittest.TestCase):
    """Test cases for subtitle track selection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_video_path = "test_video.mp4"
        self.mock_ffprobe_output = {
            "streams": [
                {
                    "index": 2,
                    "codec_type": "subtitle",
                    "codec_name": "subrip",
                    "tags": {
                        "language": "en",
                        "title": "English"
                    }
                },
                {
                    "index": 3,
                    "codec_type": "subtitle", 
                    "codec_name": "ass",
                    "tags": {
                        "language": "es",
                        "title": "Spanish"
                    }
                }
            ]
        }
    
    @patch('main.functions.subtitle_track_selector.subprocess.run')
    @patch('main.functions.subtitle_track_selector.os.path.exists')
    def test_get_subtitle_tracks_success(self, mock_exists, mock_run):
        """Test successful subtitle track detection."""
        # Mock file existence and subprocess result
        mock_exists.return_value = True
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(self.mock_ffprobe_output)
        mock_run.return_value = mock_result
        
        # Test the function
        tracks = get_subtitle_tracks(self.test_video_path)
        
        # Assertions
        self.assertEqual(len(tracks), 2)
        self.assertEqual(tracks[0]['language'], 'en')
        self.assertEqual(tracks[1]['language'], 'es')
        self.assertIn('Track 1', tracks[0]['display_name'])
        self.assertIn('English', tracks[0]['display_name'])
    
    @patch('main.functions.subtitle_track_selector.subprocess.run')
    @patch('main.functions.subtitle_track_selector.os.path.exists')
    def test_get_subtitle_tracks_no_file(self, mock_exists, mock_run):
        """Test behavior when video file doesn't exist."""
        mock_exists.return_value = False
        
        tracks = get_subtitle_tracks("nonexistent.mp4")
        
        self.assertEqual(tracks, [])
        mock_run.assert_not_called()
    
    @patch('main.functions.subtitle_track_selector.subprocess.run')
    @patch('main.functions.subtitle_track_selector.os.path.exists')
    def test_get_subtitle_tracks_ffprobe_error(self, mock_exists, mock_run):
        """Test behavior when ffprobe fails."""
        mock_exists.return_value = True
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        tracks = get_subtitle_tracks(self.test_video_path)
        
        self.assertEqual(tracks, [])
    
    def test_get_best_subtitle_track(self):
        """Test best subtitle track selection logic."""
        tracks = [
            {'language': 'es', 'index': 0},
            {'language': 'en', 'index': 1},
            {'language': 'fr', 'index': 2}
        ]
        
        # Test preferred language selection
        best_index = get_best_subtitle_track(tracks, 'en')
        self.assertEqual(best_index, 1)
        
        # Test fallback to first track
        best_index = get_best_subtitle_track(tracks, 'de')
        self.assertEqual(best_index, 0)
        
        # Test empty tracks
        best_index = get_best_subtitle_track([], 'en')
        self.assertIsNone(best_index)
    
    @patch('main.functions.subtitle_track_selector.subprocess.run')
    @patch('main.functions.subtitle_track_selector.os.path.exists')
    def test_extract_subtitle_track_success(self, mock_exists, mock_run):
        """Test successful subtitle track extraction."""
        mock_exists.side_effect = lambda path: True  # ffmpeg exists and output file created
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        success = extract_subtitle_track(
            self.test_video_path, 
            0, 
            "output.srt", 
            "subrip"
        )
        
        self.assertTrue(success)
        mock_run.assert_called_once()
    
    @patch('main.functions.subtitle_track_selector.subprocess.run')
    @patch('main.functions.subtitle_track_selector.os.path.exists')
    def test_extract_subtitle_track_failure(self, mock_exists, mock_run):
        """Test subtitle track extraction failure."""
        mock_exists.side_effect = lambda path: "ffmpeg" in path  # ffmpeg exists but output fails
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        success = extract_subtitle_track(
            self.test_video_path,
            0,
            "output.srt",
            "subrip"
        )
        
        self.assertFalse(success)

class TestEnhancedAlassIntegration(unittest.TestCase):
    """Test cases for enhanced alass integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_video_path = "test_video.mp4"
        self.test_subtitle_path = "test_subtitle.srt"
        self.test_output_path = "output.srt"
    
    @patch('main.functions.enhanced_alass_integration.get_subtitle_tracks')
    @patch('main.functions.enhanced_alass_integration.extract_subtitle_track')
    @patch('main.functions.enhanced_alass_integration.os.path.exists')
    def test_extract_best_subtitle_for_alass_auto_select(self, mock_exists, mock_extract, mock_get_tracks):
        """Test automatic subtitle extraction for alass."""
        # Mock setup
        mock_exists.return_value = True
        mock_tracks = [
            {'index': 0, 'language': 'en', 'codec_name': 'subrip'},
            {'index': 1, 'language': 'es', 'codec_name': 'ass'}
        ]
        mock_get_tracks.return_value = mock_tracks
        mock_extract.return_value = True
        
        # Test auto-selection
        result = extract_best_subtitle_for_alass(
            self.test_video_path,
            auto_select=True,
            preferred_language='en'
        )
        
        # Assertions
        self.assertIsNotNone(result)
        mock_get_tracks.assert_called_once_with(self.test_video_path)
        mock_extract.assert_called_once()
    
    @patch('main.functions.enhanced_alass_integration.get_subtitle_tracks')
    def test_extract_best_subtitle_for_alass_no_tracks(self, mock_get_tracks):
        """Test behavior when no subtitle tracks are found."""
        mock_get_tracks.return_value = []
        
        result = extract_best_subtitle_for_alass(self.test_video_path)
        
        self.assertIsNone(result)
    
    @patch('main.functions.enhanced_alass_integration.extract_best_subtitle_for_alass')
    @patch('main.functions.enhanced_alass_integration.subprocess.Popen')
    @patch('main.functions.enhanced_alass_integration.os.path.exists')
    def test_run_alass_with_subtitle_track(self, mock_exists, mock_popen, mock_extract):
        """Test running alass with subtitle track extraction."""
        # Mock setup
        mock_exists.return_value = True
        mock_extract.return_value = "extracted_subtitle.srt"
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        # Test the function
        process = run_alass_with_subtitle_track(
            self.test_video_path,
            self.test_subtitle_path,
            self.test_output_path
        )
        
        # Assertions
        self.assertEqual(process, mock_process)
        mock_extract.assert_called_once()
        mock_popen.assert_called_once()
    
    @patch('main.functions.enhanced_alass_integration.os.path.exists')
    @patch('main.functions.enhanced_alass_integration.os.remove')
    def test_cleanup_extracted_subtitle(self, mock_remove, mock_exists):
        """Test cleanup of extracted subtitle files."""
        # Test cleanup of temp file
        temp_path = os.path.join(tempfile.gettempdir(), "video_extracted_track_0.srt")
        mock_exists.return_value = True
        
        cleanup_extracted_subtitle(temp_path)
        
        mock_remove.assert_called_once_with(temp_path)
        
        # Test non-temp file (should not be removed)
        mock_remove.reset_mock()
        regular_path = "/home/user/subtitle.srt"
        
        cleanup_extracted_subtitle(regular_path)
        
        mock_remove.assert_not_called()

class TestConfigurationIntegration(unittest.TestCase):
    """Test configuration integration for subtitle track selection."""
    
    def test_config_defaults(self):
        """Test that default configuration values are set correctly."""
        from main.config import default_settings
        
        self.assertIn('subtitle_track_selection_enabled', default_settings)
        self.assertIn('preferred_subtitle_language', default_settings)
        self.assertIn('auto_select_subtitle_track', default_settings)
        
        self.assertTrue(default_settings['subtitle_track_selection_enabled'])
        self.assertEqual(default_settings['preferred_subtitle_language'], 'en')
        self.assertFalse(default_settings['auto_select_subtitle_track'])

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestSubtitleTrackSelector))
    test_suite.addTest(unittest.makeSuite(TestEnhancedAlassIntegration))
    test_suite.addTest(unittest.makeSuite(TestConfigurationIntegration))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")