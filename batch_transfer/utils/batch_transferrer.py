import logging
from datetime import datetime
from functools import partial
from main.utils.dicom_transferrer import DicomTransferrer

@dataclass
class BatchTransferrerConfig:
    archive_name: str = None
    clinical_trial_protocol_id: str = None
    clinical_trial_protocol_name: str = None
    pseudonymize: bool = True
    cleanup: bool = True

class BatchTransferrer:
    def __init__(self, dicomTransferrer: DicomTransferrer, config: BatchTransferrerConfig):
        self.dicomTransferrer = dicomTransferrer

    def _modify_dataset(self, pseudonym, ds):
        """Pseudonymize an incoming dataset with the given pseudonym and add the trial
        name to the DICOM header if specified."""

        if self.config.pseudonymize:
            self._anonymizer.anonymize_dataset(ds, patient_name=pseudonym)

        if self.config.clinical_trial_protocol_id:
            ds.ClinicalTrialProtocolID = self.config.clinical_trial_protocol_id
        
        if self.config.clinical_trial_protocol_name:
            ds.ClinicalTrialProtocolName = self.config.clinical_trial_protocol_name

    def transfer_server2server(self, data, progress_callback):
        pass

    def transfer_server2folder(self, data, progress_callback):
        pass