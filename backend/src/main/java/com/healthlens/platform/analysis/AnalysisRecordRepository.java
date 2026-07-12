package com.healthlens.platform.analysis;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface AnalysisRecordRepository extends JpaRepository<AnalysisRecord, UUID> {
    List<AnalysisRecord> findByUser_IdOrderByCreatedAtDesc(UUID userId);

    Optional<AnalysisRecord> findByIdAndUserId(UUID id, UUID userId);

    long deleteByUser_Id(UUID userId);
}
