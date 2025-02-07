from django.db import models

# Create your models here.
from django.db import models

# Main asset model representing a PV installation.
class Asset(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    # You can add additional fields like installation date, capacity, etc.
    contractual_pr = models.FloatField(help_text="Contractual Performance Ratio (%)")

    def __str__(self):
        return self.name


# Each Asset can have multiple trackers.
class Tracker(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='trackers')
    identifier = models.CharField(max_length=100)
    installed_on = models.DateField()
    # Additional fields such as orientation, tilt angle, etc.
    
    def __str__(self):
        return f"Tracker {self.identifier} for {self.asset.name}"


# Modules represent the PV panels or arrays.
class Module(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='modules')
    model_number = models.CharField(max_length=100)
    capacity_kwp = models.FloatField(help_text="Rated capacity in kWp")
    installation_date = models.DateField()
    
    def __str__(self):
        return f"Module {self.model_number} for {self.asset.name}"


# Meteo stations collect weather data (irradiance, temperature, etc.).
class MeteoStation(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='meteo_stations')
    station_name = models.CharField(max_length=100)
    installation_date = models.DateField()
    # For a first version, you might store a file path to a CSV or a log, or add fields for key measurements.
    data_log = models.FileField(upload_to='meteo_logs/', null=True, blank=True)
    
    def __str__(self):
        return f"Meteo Station {self.station_name} for {self.asset.name}"


# Seasonal Performance Ratio (PR) metrics versus contractual PR.
class SeasonalPRMetric(models.Model):
    SEASONS = [
        ('SPR', 'Spring'),
        ('SUM', 'Summer'),
        ('AUT', 'Autumn'),
        ('WIN', 'Winter'),
    ]
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='pr_metrics')
    season = models.CharField(max_length=3, choices=SEASONS)
    measured_pr = models.FloatField(help_text="Measured Performance Ratio (%)")
    # Difference between measured and contractual PR could be calculated in a method or stored.
    difference = models.FloatField(blank=True, null=True, help_text="Measured PR minus contractual PR")
    measured_date = models.DateField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Automatically compute the difference if contractual PR is available.
        if self.asset and self.asset.contractual_pr:
            self.difference = self.measured_pr - self.asset.contractual_pr
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_season_display()} PR for {self.asset.name}"
